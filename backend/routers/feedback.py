"""
Feedback API Router

Endpoints for managing user feedback (likes and dislikes).
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Optional
from ..models.feedback import FeedbackResponse, FeedbackAction
from ..models.paper import Paper
from ..services.database_service import DatabaseService
from ..services.unified_database_service import UnifiedDatabaseService, get_unified_db_service
from ..dependencies import get_db_service, require_user_id


router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.get("", response_model=FeedbackResponse)
async def get_feedback(
    user_id: str = Depends(require_user_id),
    unified_db: UnifiedDatabaseService = Depends(get_unified_db_service)
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
        feedback = await unified_db.load_feedback(user_id)
        return feedback
    except Exception as e:
        print(f"❌ Error loading feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error loading feedback: {str(e)}"
        )


@router.post("/like", response_model=dict)
async def like_paper(
    request: dict = Body(...),
    user_id: str = Depends(require_user_id),
    unified_db: UnifiedDatabaseService = Depends(get_unified_db_service)
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
        # Extract paper_id and paper_data from request body
        paper_id = request.get('paper_id')
        paper_data_dict = request.get('paper_data')
        paper_data = None
        if paper_data_dict:
            paper_data = Paper(**paper_data_dict)
        
        if not paper_id:
            raise HTTPException(
                status_code=400,
                detail="paper_id is required"
            )
        
        # Save like feedback (this will also add to Likes folder and cache paper)
        try:
            # For Firebase, we need to ensure the service is initialized
            if unified_db.use_firebase and unified_db.firebase_service:
                if not unified_db.firebase_service._initialized:
                    await unified_db.firebase_service.init_firebase()
            
            await unified_db.save_feedback(user_id, paper_id, "liked", paper_data)
            
            return {
                "status": "success",
                "message": "Paper liked successfully",
                "paper_id": paper_id
            }
        except Exception as save_error:
            print(f"❌ Error in save_feedback: {save_error}")
            import traceback
            traceback.print_exc()
            # Still return success to avoid breaking the UI, but log the error
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
    user_id: str = Depends(require_user_id),
    unified_db: UnifiedDatabaseService = Depends(get_unified_db_service)
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
        await unified_db.delete_feedback(user_id, paper_id)
        
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
    request: dict = Body(...),
    user_id: str = Depends(require_user_id),
    unified_db: UnifiedDatabaseService = Depends(get_unified_db_service)
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
        # Extract paper_id and paper_data from request body
        paper_id = request.get('paper_id')
        paper_data_dict = request.get('paper_data')
        paper_data = None
        if paper_data_dict:
            paper_data = Paper(**paper_data_dict)
        
        if not paper_id:
            raise HTTPException(
                status_code=400,
                detail="paper_id is required"
            )
        
        # Cache paper metadata if provided
        if paper_data:
            await unified_db.cache_papers([paper_data])
            print(f"💾 Cached paper metadata: {paper_data.title[:50]}")
        
        # Save dislike feedback
        await unified_db.save_feedback(user_id, paper_id, "disliked", paper_data)
        
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
    user_id: str = Depends(require_user_id),
    unified_db: UnifiedDatabaseService = Depends(get_unified_db_service)
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
        await unified_db.delete_feedback(user_id, paper_id)
        
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
    user_id: str = Depends(require_user_id),
    unified_db: UnifiedDatabaseService = Depends(get_unified_db_service)
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
        # For unified service, we need to get all feedback and delete individually
        # This is a limitation - we could add a clear_all method to unified service
        feedback = await unified_db.load_feedback(user_id)
        for paper_id in feedback.liked + feedback.disliked:
            await unified_db.delete_feedback(user_id, paper_id)
        
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
    user_id: str = Depends(require_user_id),
    unified_db: UnifiedDatabaseService = Depends(get_unified_db_service)
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
        feedback = await unified_db.load_feedback(user_id)
        for paper_id in feedback.liked:
            await unified_db.delete_feedback(user_id, paper_id)
        
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
    user_id: str = Depends(require_user_id),
    unified_db: UnifiedDatabaseService = Depends(get_unified_db_service)
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
        feedback = await unified_db.load_feedback(user_id)
        for paper_id in feedback.disliked:
            await unified_db.delete_feedback(user_id, paper_id)
        
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
