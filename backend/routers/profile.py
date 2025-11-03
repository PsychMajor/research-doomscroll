"""
Profile API Router

Endpoints for managing user profile (topics, authors, folders).
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models.user import UserProfile
from ..services.database_service import DatabaseService
from ..dependencies import get_db_service, require_user_id


router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("", response_model=UserProfile)
async def get_profile(
    user_id: int = Depends(require_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Get current user's profile
    
    Returns the user's profile including:
    - Topics: List of research topic keywords
    - Authors: List of author names to follow
    - Folders: List of folders with papers
    
    **Returns:**
    UserProfile object with topics, authors, and folders
    
    **Example:**
    ```
    GET /api/profile
    ```
    """
    try:
        profile = await db.load_profile(user_id=user_id)
        return profile
    except Exception as e:
        print(f"❌ Error loading profile: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error loading profile: {str(e)}"
        )


@router.put("", response_model=dict)
async def update_profile(
    topics: List[str] = [],
    authors: List[str] = [],
    user_id: int = Depends(require_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Update user's profile (topics and authors)
    
    Updates the user's research interests and followed authors.
    Folders are managed through separate endpoints.
    
    **Body Parameters:**
    - `topics`: Array of topic keywords (e.g., ["machine learning", "neural networks"])
    - `authors`: Array of author names (e.g., ["John Smith", "Jane Doe"])
    
    **Returns:**
    Success status message
    
    **Example:**
    ```
    PUT /api/profile
    {
      "topics": ["quantum computing", "cryptography"],
      "authors": ["John Preskill", "Peter Shor"]
    }
    ```
    """
    try:
        await db.save_profile(topics, authors, user_id=user_id)
        return {
            "status": "success",
            "message": "Profile updated successfully",
            "topics": topics,
            "authors": authors
        }
    except Exception as e:
        print(f"❌ Error updating profile: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating profile: {str(e)}"
        )


@router.delete("", response_model=dict)
async def clear_profile(
    user_id: int = Depends(require_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Clear user's profile (topics and authors)
    
    Removes all topics and authors from the user's profile.
    Folders are preserved.
    
    **Returns:**
    Success status message
    
    **Example:**
    ```
    DELETE /api/profile
    ```
    """
    try:
        await db.save_profile([], [], user_id=user_id)
        return {
            "status": "success",
            "message": "Profile cleared successfully"
        }
    except Exception as e:
        print(f"❌ Error clearing profile: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing profile: {str(e)}"
        )
