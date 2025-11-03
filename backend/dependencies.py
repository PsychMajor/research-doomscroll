"""
FastAPI Dependencies

Shared dependencies for authentication, database access, and service injection.
"""

from typing import Optional, Dict, Any
from fastapi import Request, Depends, HTTPException, status
from .services.database_service import DatabaseService
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


def get_user_id(request: Request) -> Optional[int]:
    """
    Get user ID from session
    
    Returns user_id (int) if logged in, None if anonymous.
    Useful for optional authentication scenarios.
    
    Args:
        request: FastAPI request object with session
    
    Returns:
        User ID (int) or None if anonymous
    """
    user = request.session.get('user')
    if user and user.get('id') != 'anonymous':
        user_id = user.get('id')
        # Handle both string and int IDs
        if isinstance(user_id, str) and user_id.isdigit():
            return int(user_id)
        elif isinstance(user_id, int):
            return user_id
    return None


def require_user_id(request: Request) -> int:
    """
    Get user ID from session (required)
    
    Raises 401 if user is not logged in.
    Use this for endpoints that require user ID.
    
    Args:
        request: FastAPI request object with session
    
    Returns:
        User ID (int)
    
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
