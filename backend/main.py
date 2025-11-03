"""
Main FastAPI application entry point
Modular backend with clean architecture
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
import nltk

from .config import get_settings
import database  # Using existing database module for now

# Initialize settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Research Doomscroll API",
    description="Infinite scroll through research papers",
    version="2.0.0"
)

# Add session middleware for OAuth
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

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
    await database.init_db()
    print("✅ Database initialized")
    
    # Download required NLTK data
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)
        print("✅ NLTK data loaded")
    except Exception as e:
        print(f"⚠️  NLTK data download warning: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown"""
    await database.close_db()
    print("✅ Database connections closed")


# Mount static files (for legacy frontend - will be removed later)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates (for legacy frontend - will be removed later)
templates = Jinja2Templates(directory="templates")


# Import and include routers
from .routers import papers

# Include API routers
app.include_router(papers.router)

# TODO: Add remaining routers as we create them
# from .routers import auth, profile, folders, feedback, analytics
# app.include_router(auth.router)
# app.include_router(profile.router)
# app.include_router(folders.router)
# app.include_router(feedback.router)
# app.include_router(analytics.router)


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
