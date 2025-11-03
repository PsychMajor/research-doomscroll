"""
Feedback API Router

Endpoints for managing user feedback (likes and dislikes).
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Optional
from ..models.feedback import FeedbackResponse, FeedbackAction
from ..models.paper import Paper
from ..services.database_service import DatabaseService
from ..dependencies import get_db_service, require_user_id


router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.get("", response_model=FeedbackResponse)
async def get_feedback(
    user_id: int = Depends(require_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Get user's feedback (liked and disliked papers)
    
    Returns all paper IDs that the user has liked or disliked.
    
    **Returns:**
    FeedbackResponse with:
    - liked: Array of liked paper IDs
    - disliked: Array of disliked paper IDs
    
    **Example:**
    ```
    GET /api/feedback
    ```
    """
    try:
        feedback = await db.load_feedback(user_id=user_id)
        return feedback
    except Exception as e:
        print(f"❌ Error loading feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error loading feedback: {str(e)}"
        )


@router.post("/like", response_model=dict)
async def like_paper(
    paper_id: str,
    paper_data: Optional[Paper] = Body(None),
    user_id: int = Depends(require_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Like a paper
    
    Marks a paper as liked by the user. Optionally caches paper metadata
    for faster retrieval later.
    
    **Body Parameters:**
    - `paper_id`: OpenAlex paper ID (required)
    - `paper_data`: Full paper object for caching (optional)
    
    **Returns:**
    Success status message
    
    **Example:**
    ```
    POST /api/feedback/like
    {
      "paper_id": "W2104477830",
      "paper_data": {...}  // optional Paper object
    }
    ```
    """
    try:
        # Cache paper metadata if provided
        if paper_data:
            await db.save_paper(paper_data)
            print(f"💾 Cached paper metadata: {paper_data.title[:50]}")
        
        # Save like feedback
        await db.save_feedback(paper_id, "liked", user_id=user_id)
        
        return {
            "status": "success",
            "message": "Paper liked successfully",
            "paper_id": paper_id
        }
    except Exception as e:
        print(f"❌ Error liking paper: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error liking paper: {str(e)}"
        )


@router.delete("/like/{paper_id}", response_model=dict)
async def unlike_paper(
    paper_id: str,
    user_id: int = Depends(require_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Unlike a paper
    
    Removes the like from a paper.
    
    **Path Parameters:**
    - `paper_id`: OpenAlex paper ID
    
    **Returns:**
    Success status message
    
    **Example:**
    ```
    DELETE /api/feedback/like/W2104477830
    ```
    """
    try:
        await db.delete_feedback(paper_id, user_id=user_id)
        
        return {
            "status": "success",
            "message": "Paper unliked successfully",
            "paper_id": paper_id
        }
    except Exception as e:
        print(f"❌ Error unliking paper: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error unliking paper: {str(e)}"
        )


@router.post("/dislike", response_model=dict)
async def dislike_paper(
    paper_id: str,
    paper_data: Optional[Paper] = Body(None),
    user_id: int = Depends(require_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Dislike a paper
    
    Marks a paper as disliked by the user. Optionally caches paper metadata.
    
    **Body Parameters:**
    - `paper_id`: OpenAlex paper ID (required)
    - `paper_data`: Full paper object for caching (optional)
    
    **Returns:**
    Success status message
    
    **Example:**
    ```
    POST /api/feedback/dislike
    {
      "paper_id": "W2104477830",
      "paper_data": {...}  // optional
    }
    ```
    """
    try:
        # Cache paper metadata if provided
        if paper_data:
            await db.save_paper(paper_data)
            print(f"💾 Cached paper metadata: {paper_data.title[:50]}")
        
        # Save dislike feedback
        await db.save_feedback(paper_id, "disliked", user_id=user_id)
        
        return {
            "status": "success",
            "message": "Paper disliked successfully",
            "paper_id": paper_id
        }
    except Exception as e:
        print(f"❌ Error disliking paper: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error disliking paper: {str(e)}"
        )


@router.delete("/dislike/{paper_id}", response_model=dict)
async def undislike_paper(
    paper_id: str,
    user_id: int = Depends(require_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Remove dislike from a paper
    
    Removes the dislike from a paper.
    
    **Path Parameters:**
    - `paper_id`: OpenAlex paper ID
    
    **Returns:**
    Success status message
    
    **Example:**
    ```
    DELETE /api/feedback/dislike/W2104477830
    ```
    """
    try:
        await db.delete_feedback(paper_id, user_id=user_id)
        
        return {
            "status": "success",
            "message": "Dislike removed successfully",
            "paper_id": paper_id
        }
    except Exception as e:
        print(f"❌ Error removing dislike: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error removing dislike: {str(e)}"
        )


@router.delete("", response_model=dict)
async def clear_all_feedback(
    user_id: int = Depends(require_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Clear all user feedback
    
    Removes all likes and dislikes from the user's account.
    
    **Returns:**
    Success status message
    
    **Example:**
    ```
    DELETE /api/feedback
    ```
    """
    try:
        await db.clear_all_feedback(action=None, user_id=user_id)
        
        return {
            "status": "success",
            "message": "All feedback cleared successfully"
        }
    except Exception as e:
        print(f"❌ Error clearing feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing feedback: {str(e)}"
        )


@router.delete("/liked", response_model=dict)
async def clear_liked(
    user_id: int = Depends(require_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Clear all liked papers
    
    Removes all likes from the user's account.
    Disliked papers are preserved.
    
    **Returns:**
    Success status message
    
    **Example:**
    ```
    DELETE /api/feedback/liked
    ```
    """
    try:
        await db.clear_all_feedback(action="liked", user_id=user_id)
        
        return {
            "status": "success",
            "message": "All likes cleared successfully"
        }
    except Exception as e:
        print(f"❌ Error clearing likes: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing likes: {str(e)}"
        )


@router.delete("/disliked", response_model=dict)
async def clear_disliked(
    user_id: int = Depends(require_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Clear all disliked papers
    
    Removes all dislikes from the user's account.
    Liked papers are preserved.
    
    **Returns:**
    Success status message
    
    **Example:**
    ```
    DELETE /api/feedback/disliked
    ```
    """
    try:
        await db.clear_all_feedback(action="disliked", user_id=user_id)
        
        return {
            "status": "success",
            "message": "All dislikes cleared successfully"
        }
    except Exception as e:
        print(f"❌ Error clearing dislikes: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing dislikes: {str(e)}"
        )
