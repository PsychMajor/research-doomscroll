"""
FastAPI Dependencies

Shared dependencies for authentication, database access, and service injection.
"""

from typing import Optional, Dict, Any
from fastapi import Request, Depends, HTTPException, status
from .services.database_service import DatabaseService
from .services.unified_database_service import UnifiedDatabaseService, get_unified_db_service
from .services.openalex_service import OpenAlexService


# ==================== Database Service ====================

# Global database service instance
_db_service: Optional[DatabaseService] = None


async def get_db_service() -> DatabaseService:
    """
    Dependency injection for DatabaseService
    
    Returns singleton database service instance.
    """
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
        await _db_service.init_db()
    return _db_service


# ==================== OpenAlex Service ====================

def get_openalex_service() -> OpenAlexService:
    """
    Dependency injection for OpenAlexService
    
    Returns new OpenAlexService instance (stateless).
    """
    return OpenAlexService()


# ==================== Authentication ====================

def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Get current user from session
    
    Returns user dict from session or anonymous user if not logged in.
    This allows the API to work without authentication (public access).
    
    Args:
        request: FastAPI request object with session
    
    Returns:
        User dict with id, email, name, picture
    """
    user = request.session.get('user')
    if user:
        return user
    
    # Return anonymous user for public access
    return {
        'id': 'anonymous',
        'email': 'anonymous@example.com',
        'name': 'Anonymous User',
        'picture': ''
    }


def get_authenticated_user(request: Request) -> Dict[str, Any]:
    """
    Get authenticated user from session (required)
    
    Raises 401 if user is not logged in.
    Use this for endpoints that require authentication.
    
    Args:
        request: FastAPI request object with session
    
    Returns:
        User dict with id, email, name, picture
    
    Raises:
        HTTPException: 401 if user not authenticated
    """
    user = request.session.get('user')
    if not user or user.get('id') == 'anonymous':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return user


def get_user_id(request: Request) -> Optional[str]:
    """
    Get user ID from session
    
    Returns user_id (string) if logged in, None if anonymous.
    For Firebase, this is Google UID. For PostgreSQL, this is converted to string.
    Useful for optional authentication scenarios.
    
    Args:
        request: FastAPI request object with session
    
    Returns:
        User ID (string) or None if anonymous
    """
    user = request.session.get('user')
    if user and user.get('id') != 'anonymous':
        user_id = user.get('id')
        # Return as string (works for both Firebase UIDs and PostgreSQL IDs)
        return str(user_id) if user_id else None
    return None


def get_google_uid(request: Request) -> Optional[str]:
    """
    Get Google UID from session (for Firebase)
    
    Returns Google UID if available, otherwise falls back to user ID.
    
    Args:
        request: FastAPI request object with session
    
    Returns:
        Google UID (string) or None if anonymous
    """
    user = request.session.get('user')
    if user and user.get('id') != 'anonymous':
        # Prefer google_uid if available, otherwise use id
        return user.get('google_uid') or str(user.get('id'))
    return None


def require_user_id(request: Request) -> str:
    """
    Get user ID from session (required)
    
    Raises 401 if user is not logged in.
    Use this for endpoints that require user ID.
    Returns string ID (works for both Firebase UIDs and PostgreSQL IDs).
    
    Args:
        request: FastAPI request object with session
    
    Returns:
        User ID (string)
    
    Raises:
        HTTPException: 401 if user not authenticated
    """
    user_id = get_user_id(request)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return user_id
