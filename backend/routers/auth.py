"""
Authentication Router

Handles Google OAuth login, callback, and logout endpoints.
Maintains session-based authentication for compatibility with existing frontend.
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth
from typing import Dict, Optional
import os

from ..services.database_service import DatabaseService
from ..dependencies import get_db_service, get_current_user

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Configure OAuth (same as legacy app.py)
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)


@router.get("/login")
async def login(request: Request):
    """
    Initiate Google OAuth login flow.
    
    Redirects user to Google's OAuth consent screen.
    After authorization, Google redirects back to /api/auth/callback.
    
    Returns:
        RedirectResponse to Google OAuth
    """
    # Build callback URL dynamically based on request
    redirect_uri = request.url_for('auth_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def auth_callback(
    request: Request,
    db: DatabaseService = Depends(get_db_service)
):
    """
    Handle OAuth callback from Google.
    
    Receives authorization code, exchanges for access token,
    retrieves user info, and creates/updates user in database.
    Stores user information in session for subsequent requests.
    
    Args:
        request: FastAPI request with OAuth code in query params
        db: Database service dependency
    
    Returns:
        RedirectResponse to homepage with user logged in
    
    Raises:
        HTTPException: If OAuth token exchange fails
    """
    try:
        # Exchange authorization code for access token
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            raise HTTPException(
                status_code=400,
                detail="Failed to retrieve user information from Google"
            )
        
        # Create or update user in database
        db_user_id = await db.create_or_update_user(
            email=user_info['email'],
            name=user_info.get('name', ''),
            picture_url=user_info.get('picture', '')
        )
        
        # Store user in session
        # Use database user_id if available, fallback to Google sub ID
        request.session['user'] = {
            'id': db_user_id if db_user_id else user_info['sub'],
            'email': user_info['email'],
            'name': user_info.get('name', ''),
            'picture': user_info.get('picture', '')
        }
        
        print(f"✅ User logged in: {user_info['email']} (DB ID: {db_user_id})")
        
    except Exception as e:
        print(f"❌ OAuth error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Authentication failed: {str(e)}"
        )
    
    # Redirect to homepage after successful login
    return RedirectResponse(url='/')


@router.get("/logout")
async def logout(request: Request):
    """
    Logout current user by clearing session.
    
    Removes user information from session storage and redirects to homepage.
    User will need to login again to access authenticated features.
    
    Returns:
        RedirectResponse to homepage
    """
    user_email = request.session.get('user', {}).get('email', 'Unknown')
    request.session.pop('user', None)
    
    print(f"👋 User logged out: {user_email}")
    
    return RedirectResponse(url='/')


@router.get("/me")
async def get_current_user_info(user: Optional[Dict] = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Useful for frontend to check authentication status and display user details.
    Returns null if no user is logged in (allows anonymous access).
    
    Returns:
        User object with id, email, name, picture or null if not authenticated
    
    Example Response:
        {
            "id": 123,
            "email": "user@example.com",
            "name": "John Doe",
            "picture": "https://..."
        }
    """
    if not user:
        return JSONResponse(content=None)
    
    return JSONResponse(content=user)


@router.get("/status")
async def auth_status(request: Request):
    """
    Check if user is authenticated.
    
    Simple boolean check for authentication status.
    Useful for frontend to conditionally render UI elements.
    
    Returns:
        {"authenticated": true/false, "user": {...} or null}
    
    Example Response:
        {
            "authenticated": true,
            "user": {
                "id": 123,
                "email": "user@example.com",
                "name": "John Doe"
            }
        }
    """
    user = request.session.get('user')
    
    return {
        "authenticated": user is not None,
        "user": user
    }
