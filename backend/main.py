"""
Main FastAPI application entry point
Modular backend with clean architecture
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
import nltk

from .config import get_settings
from .dependencies import get_db_service
from .services.unified_database_service import get_unified_db_service

# Initialize settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Research Doomscroll API",
    description="Infinite scroll through research papers",
    version="2.0.0"
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware for OAuth with proper cookie settings
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie="session",
    max_age=14 * 24 * 60 * 60,  # 14 days
    same_site="lax",
    https_only=False  # Set to True in production with HTTPS
)

# Configure OAuth
oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)


@app.on_event("startup")
async def startup_event():
    """Initialize database connection pool and load NLTK data on startup"""
    # Initialize unified database service (PostgreSQL or Firebase)
    unified_db = await get_unified_db_service()
    print("✅ Unified database service initialized")
    
    # Also initialize legacy PostgreSQL service for backward compatibility
    if not settings.use_firebase:
        db_service = await get_db_service()
        print("✅ Legacy PostgreSQL database initialized")
    
    # Download required NLTK data (with SSL certificate fix for macOS)
    try:
        import ssl
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context
        
        # Try to download NLTK data
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('punkt_tab', quiet=True)
            print("✅ NLTK data loaded")
        except Exception as nltk_error:
            # If download fails, try to use existing data or continue without it
            print(f"⚠️  NLTK data download warning: {nltk_error}")
            print("   Continuing without NLTK data (text processing may be limited)")
    except Exception as e:
        print(f"⚠️  NLTK setup warning: {e}")
        print("   Continuing without NLTK data (text processing may be limited)")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown"""
    # Database service will handle cleanup
    print("✅ Shutting down")


# Mount static files (for legacy frontend - will be removed later)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates (for legacy frontend - will be removed later)
templates = Jinja2Templates(directory="templates")


# Import and include routers
from .routers import papers, profile, feedback, folders, auth, analytics, proxy, autocomplete

# Include API routers
app.include_router(papers.router)
app.include_router(profile.router)
app.include_router(feedback.router)
app.include_router(folders.router)
app.include_router(auth.router)
app.include_router(analytics.router)
app.include_router(proxy.router)
app.include_router(autocomplete.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Research Doomscroll API v2.0",
        "status": "Backend refactoring in progress",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
