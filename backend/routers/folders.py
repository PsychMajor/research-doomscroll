"""
Folders API Router

Endpoints for managing user folders and organizing papers.
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict, Any
from pydantic import BaseModel
from ..models.folder import Folder, FolderCreate, FolderUpdate, AddPaperToFolder
from ..models.paper import Paper
from ..services.database_service import DatabaseService
from ..dependencies import get_db_service, require_user_id
import uuid


router = APIRouter(prefix="/api/folders", tags=["folders"])


@router.get("", response_model=List[Folder])
async def get_folders(
    user_id: int = Depends(require_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Get all user's folders
    
    Returns all folders with their papers.
    
    **Returns:**
    Array of Folder objects with papers
    
    **Example:**
    ```
    GET /api/folders
    ```
    """
    try:
        profile = await db.load_profile(user_id=user_id)
        folders = profile.folders
        
        # Convert to Folder models
        folder_models = []
        for folder_dict in folders:
            folder_models.append(Folder(**folder_dict))
        
        return folder_models
    except Exception as e:
        print(f"❌ Error loading folders: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error loading folders: {str(e)}"
        )


@router.post("", response_model=Folder)
async def create_folder(
    folder: FolderCreate,
    user_id: int = Depends(require_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Create a new folder
    
    Creates a new folder for organizing papers.
    
    **Body Parameters:**
    - `name`: Folder name (required)
    
    **Returns:**
    Created Folder object
    
    **Example:**
    ```
    POST /api/folders
    {
      "name": "Important Papers"
    }
    ```
    """
    try:
        # Load current folders
        profile = await db.load_profile(user_id=user_id)
        folders = profile.folders
        
        # Generate unique ID for new folder
        new_folder_id = str(uuid.uuid4())
        
        # Create new folder
        new_folder = {
            "id": new_folder_id,
            "name": folder.name,
            "papers": []
        }
        
        folders.append(new_folder)
        
        # Save updated folders
        await db.save_folders(folders, user_id=user_id)
        
        print(f"📁 Created folder: {folder.name} (ID: {new_folder_id})")
        
        return Folder(**new_folder)
    except Exception as e:
        print(f"❌ Error creating folder: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating folder: {str(e)}"
        )


@router.get("/{folder_id}", response_model=Folder)
async def get_folder(
    folder_id: str,
    user_id: int = Depends(require_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Get a specific folder by ID
    
    Returns folder details with all papers.
    
    **Path Parameters:**
    - `folder_id`: Folder ID
    
    **Returns:**
    Folder object with papers
    
    **Example:**
    ```
    GET /api/folders/123e4567-e89b-12d3-a456-426614174000
    ```
    """
    try:
        profile = await db.load_profile(user_id=user_id)
        folders = profile.folders
        
        # Find the folder
        folder_dict = next((f for f in folders if f['id'] == folder_id), None)
        
        if not folder_dict:
            raise HTTPException(
                status_code=404,
                detail=f"Folder with ID '{folder_id}' not found"
            )
        
        return Folder(**folder_dict)
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting folder: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting folder: {str(e)}"
        )


@router.put("/{folder_id}", response_model=Folder)
async def update_folder(
    folder_id: str,
    folder_update: FolderUpdate,
    user_id: int = Depends(require_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Update a folder's name
    
    Updates folder metadata (currently only name).
    
    **Path Parameters:**
    - `folder_id`: Folder ID
    
    **Body Parameters:**
    - `name`: New folder name (required)
    
    **Returns:**
    Updated Folder object
    
    **Example:**
    ```
    PUT /api/folders/123e4567-e89b-12d3-a456-426614174000
    {
      "name": "Updated Folder Name"
    }
    ```
    """
    try:
        # Cannot rename the default "Likes" folder
        if folder_id.lower() == 'likes':
            raise HTTPException(
                status_code=400,
                detail="Cannot rename the 'Likes' folder"
            )
        
        profile = await db.load_profile(user_id=user_id)
        folders = profile.folders
        
        # Find and update the folder
        folder_found = False
        for folder in folders:
            if folder['id'] == folder_id:
                folder['name'] = folder_update.name
                folder_found = True
                break
        
        if not folder_found:
            raise HTTPException(
                status_code=404,
                detail=f"Folder with ID '{folder_id}' not found"
            )
        
        # Save updated folders
        await db.save_folders(folders, user_id=user_id)
        
        print(f"✏️  Updated folder {folder_id}: {folder_update.name}")
        
        # Return updated folder
        updated_folder = next(f for f in folders if f['id'] == folder_id)
        return Folder(**updated_folder)
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error updating folder: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating folder: {str(e)}"
        )


@router.delete("/{folder_id}", response_model=dict)
async def delete_folder(
    folder_id: str,
    user_id: int = Depends(require_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Delete a folder
    
    Removes a folder and all its contents.
    The default "Likes" folder cannot be deleted.
    
    **Path Parameters:**
    - `folder_id`: Folder ID
    
    **Returns:**
    Success status message
    
    **Example:**
    ```
    DELETE /api/folders/123e4567-e89b-12d3-a456-426614174000
    ```
    """
    try:
        # Cannot delete the default "Likes" folder
        if folder_id.lower() == 'likes':
            raise HTTPException(
                status_code=400,
                detail="Cannot delete the 'Likes' folder"
            )
        
        profile = await db.load_profile(user_id=user_id)
        folders = profile.folders
        
        # Filter out the folder to delete
        initial_count = len(folders)
        folders = [f for f in folders if f['id'] != folder_id]
        
        if len(folders) == initial_count:
            raise HTTPException(
                status_code=404,
                detail=f"Folder with ID '{folder_id}' not found"
            )
        
        # Save updated folders
        await db.save_folders(folders, user_id=user_id)
        
        print(f"🗑️  Deleted folder: {folder_id}")
        
        return {
            "status": "success",
            "message": "Folder deleted successfully",
            "folder_id": folder_id
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error deleting folder: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting folder: {str(e)}"
        )


@router.post("/{folder_id}/papers", response_model=dict)
async def add_paper_to_folder(
    folder_id: str,
    paper_id: str = Body(...),
    paper_data: Paper = Body(...),
    user_id: int = Depends(require_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Add a paper to a folder
    
    Adds a paper to the specified folder.
    If adding to the "Likes" folder, also records as a like.
    
    **Path Parameters:**
    - `folder_id`: Folder ID
    
    **Body Parameters:**
    - `paper_id`: Paper ID (required)
    - `paper_data`: Full paper object (required for caching)
    
    **Returns:**
    Success status message
    
    **Example:**
    ```
    POST /api/folders/123e4567-e89b-12d3-a456-426614174000/papers
    {
      "paper_id": "W2104477830",
      "paper_data": {...}
    }
    ```
    """
    try:
        # Load user's folders
        profile = await db.load_profile(user_id=user_id)
        folders = profile.folders
        
        # Find the target folder
        folder_found = False
        for folder in folders:
            if folder['id'] == folder_id:
                # Ensure papers array exists
                if 'papers' not in folder:
                    folder['papers'] = []
                
                # Check if paper already exists
                if not any(p.get('paperId') == paper_id for p in folder['papers']):
                    folder['papers'].append(paper_data.model_dump())
                    folder_found = True
                    print(f"📁 Added paper {paper_id} to folder {folder_id}")
                else:
                    print(f"ℹ️  Paper {paper_id} already in folder {folder_id}")
                    folder_found = True
                break
        
        if not folder_found:
            raise HTTPException(
                status_code=404,
                detail=f"Folder with ID '{folder_id}' not found"
            )
        
        # Save updated folders
        await db.save_folders(folders, user_id=user_id)
        
        # Cache paper metadata
        await db.save_paper(paper_data)
        
        # If adding to "likes" folder, also record as a like
        if folder_id.lower() == 'likes':
            await db.save_feedback(paper_id, "liked", user_id=user_id)
            print(f"❤️  Also recorded paper {paper_id} as liked")
        
        return {
            "status": "success",
            "message": "Paper added to folder",
            "folder_id": folder_id,
            "paper_id": paper_id
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error adding paper to folder: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error adding paper to folder: {str(e)}"
        )


@router.delete("/{folder_id}/papers/{paper_id}", response_model=dict)
async def remove_paper_from_folder(
    folder_id: str,
    paper_id: str,
    user_id: int = Depends(require_user_id),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Remove a paper from a folder
    
    Removes a paper from the specified folder.
    If removing from the "Likes" folder, also unlikes the paper.
    
    **Path Parameters:**
    - `folder_id`: Folder ID
    - `paper_id`: Paper ID
    
    **Returns:**
    Success status message
    
    **Example:**
    ```
    DELETE /api/folders/123e4567-e89b-12d3-a456-426614174000/papers/W2104477830
    ```
    """
    try:
        # Load user's folders
        profile = await db.load_profile(user_id=user_id)
        folders = profile.folders
        
        # Find the target folder and remove paper
        folder_found = False
        for folder in folders:
            if folder['id'] == folder_id:
                if 'papers' in folder:
                    initial_count = len(folder['papers'])
                    folder['papers'] = [p for p in folder['papers'] if p.get('paperId') != paper_id]
                    
                    if len(folder['papers']) < initial_count:
                        print(f"🗑️  Removed paper {paper_id} from folder {folder_id}")
                    else:
                        print(f"ℹ️  Paper {paper_id} not found in folder {folder_id}")
                    
                folder_found = True
                break
        
        if not folder_found:
            raise HTTPException(
                status_code=404,
                detail=f"Folder with ID '{folder_id}' not found"
            )
        
        # Save updated folders
        await db.save_folders(folders, user_id=user_id)
        
        # If removing from "likes" folder, also unlike it
        if folder_id.lower() == 'likes':
            await db.delete_feedback(paper_id, user_id=user_id)
            print(f"💔 Also unliked paper {paper_id}")
        
        return {
            "status": "success",
            "message": "Paper removed from folder",
            "folder_id": folder_id,
            "paper_id": paper_id
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error removing paper from folder: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error removing paper from folder: {str(e)}"
        )
