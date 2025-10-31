from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv
import os
import database

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Add session middleware for OAuth
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production-use-python-secrets")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Configure OAuth
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@app.on_event("startup")
async def startup_event():
    """Initialize database connection pool on startup"""
    await database.init_db()
    print("✅ Database initialized")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

def get_current_user(request: Request):
    """Get current user from session, return anonymous user if not logged in"""
    user = request.session.get('user')
    if user:
        return user
    # Return anonymous user
    return {
        'id': 'anonymous',
        'email': 'anonymous@example.com',
        'name': 'Anonymous User',
        'picture': ''
    }

@app.get("/login")
async def login(request: Request):
    """Initiate Google OAuth login"""
    redirect_uri = request.url_for('auth_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Handle OAuth callback"""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if user_info:
            # Store user in session
            request.session['user'] = {
                'id': user_info['sub'],
                'email': user_info['email'],
                'name': user_info.get('name', ''),
                'picture': user_info.get('picture', '')
            }
            
            # Create or update user in database
            await database.create_or_update_user(
                user_id=user_info['sub'],
                email=user_info['email'],
                name=user_info.get('name', ''),
                picture=user_info.get('picture', '')
            )
    except Exception as e:
        print(f"OAuth error: {e}")
    
    return RedirectResponse(url='/')

@app.get("/logout")
async def logout(request: Request):
    """Logout user"""
    request.session.pop('user', None)
    return RedirectResponse(url='/')

# ============================================================================
# MAIN ROUTES
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main homepage"""
    user = get_current_user(request)
    user_id = user['id']
    
    # Load user's profile and feedback
    profile = await database.load_profile(user_id=user_id)
    feedback = await database.load_feedback(user_id=user_id)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "papers": [],
        "show_form": True,
        "topics": ", ".join(profile.get("topics", [])),
        "authors": ", ".join(profile.get("authors", [])),
        "profile": profile,
        "feedback": feedback
    })

@app.get("/likes", response_class=HTMLResponse)
async def get_likes(request: Request):
    """Display all liked papers"""
    user = get_current_user(request)
    user_id = user['id']
    
    # Load user's feedback
    feedback = await database.load_feedback(user_id=user_id)
    profile = await database.load_profile(user_id=user_id)
    
    return templates.TemplateResponse("likes.html", {
        "request": request,
        "user": user,
        "papers": [],
        "liked_paper_ids": feedback.get('liked', []),
        "feedback": feedback,
        "profile": profile,
        "show_form": False
    })

# ============================================================================
# PROFILE ROUTES
# ============================================================================

@app.post("/profile/save")
async def save_profile_endpoint(request: Request, topics: str = Form(""), authors: str = Form("")):
    """Save user profile"""
    user = get_current_user(request)
    user_id = user['id']
    
    topics_list = [t.strip() for t in topics.split(',') if t.strip()]
    authors_list = [a.strip() for a in authors.split(',') if a.strip()]
    
    await database.save_profile(topics_list, authors_list, user_id=user_id)
    
    # Redirect to home
    if topics or authors:
        return RedirectResponse(url=f"/?topics={topics}&authors={authors}", status_code=303)
    return RedirectResponse(url="/", status_code=303)

@app.get("/profile")
async def get_profile(request: Request):
    """Get current profile as JSON"""
    user = get_current_user(request)
    return await database.load_profile(user_id=user['id'])

@app.post("/profile/clear")
async def clear_profile_endpoint(request: Request):
    """Clear user profile"""
    user = get_current_user(request)
    await database.save_profile([], [], user_id=user['id'])
    return RedirectResponse(url="/", status_code=303)

# ============================================================================
# FEEDBACK ROUTES (Like/Dislike)
# ============================================================================

@app.post("/paper/like")
async def like_paper_endpoint(request: Request, paper_id: str = Form(...)):
    """Like a paper"""
    user = get_current_user(request)
    await database.like_paper(paper_id, user_id=user['id'])
    return {"status": "success"}

@app.post("/paper/unlike")
async def unlike_paper_endpoint(request: Request, paper_id: str = Form(...)):
    """Unlike a paper"""
    user = get_current_user(request)
    await database.unlike_paper(paper_id, user_id=user['id'])
    return {"status": "success"}

@app.post("/paper/dislike")
async def dislike_paper_endpoint(request: Request, paper_id: str = Form(...)):
    """Dislike a paper"""
    user = get_current_user(request)
    await database.dislike_paper(paper_id, user_id=user['id'])
    return {"status": "success"}

@app.post("/paper/undislike")
async def undislike_paper_endpoint(request: Request, paper_id: str = Form(...)):
    """Undislike a paper"""
    user = get_current_user(request)
    await database.undislike_paper(paper_id, user_id=user['id'])
    return {"status": "success"}

@app.get("/feedback")
async def get_feedback_endpoint(request: Request):
    """Get user feedback as JSON"""
    user = get_current_user(request)
    return await database.load_feedback(user_id=user['id'])

@app.post("/feedback/clear")
async def clear_all_feedback_endpoint(request: Request):
    """Clear all user feedback"""
    user = get_current_user(request)
    await database.clear_feedback(user_id=user['id'])
    return RedirectResponse(url="/", status_code=303)

@app.post("/feedback/clear/liked")
async def clear_liked_endpoint(request: Request):
    """Clear liked papers"""
    user = get_current_user(request)
    await database.clear_liked(user_id=user['id'])
    return RedirectResponse(url="/", status_code=303)

@app.post("/feedback/clear/disliked")
async def clear_disliked_endpoint(request: Request):
    """Clear disliked papers"""
    user = get_current_user(request)
    await database.clear_disliked(user_id=user['id'])
    return RedirectResponse(url="/", status_code=303)

# ============================================================================
# TRACKING ROUTES (Optional analytics)
# ============================================================================

@app.post("/card/visible")
async def log_card_visible(request: Request, card_number: int = Form(...), paper_id: str = Form(...)):
    """Log when a card becomes visible"""
    print(f"👁️  Card #{card_number} is now visible (Paper ID: {paper_id})")
    return {"status": "success"}

@app.post("/card/second-to-last")
async def log_second_to_last(request: Request, card_number: int = Form(...), paper_id: str = Form(...), total_cards: int = Form(...)):
    """Log when user views second-to-last card"""
    print(f"🔔 SECOND-TO-LAST CARD: User viewing card #{card_number} (Paper ID: {paper_id}) - {card_number} of {total_cards} cards")
    return {"status": "success"}
