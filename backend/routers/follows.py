"""
Follows API Router

Endpoints for following/unfollowing authors, institutions, topics, and sources.
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict, Any
from pydantic import BaseModel

from ..services.follow_service import FollowService
from ..services.firebase_service import FirebaseService, get_firebase_service
from ..services.openalex_service import OpenAlexService
from ..dependencies import get_current_user, get_openalex_service, get_google_uid
from ..utils.gpt_query_parser import parse_search_query_with_gpt
from ..config import get_settings
import os
import json


router = APIRouter(prefix="/api/follows", tags=["follows"])


class FollowEntityRequest(BaseModel):
    type: str  # "author", "institution", "topic", "source", or "custom"
    entityId: str  # OpenAlex entity ID (short form) or parsed query JSON for custom
    entityName: str  # Display name
    openalexId: str  # Full OpenAlex ID (e.g., "https://openalex.org/A1234567890") or query string for custom


def get_follow_service(
    firebase_service: FirebaseService = Depends(get_firebase_service),
    openalex_service: OpenAlexService = Depends(get_openalex_service)
) -> FollowService:
    """Dependency to get follow service instance"""
    return FollowService(firebase_service, openalex_service)


@router.post("")
async def follow_entity(
    request: FollowEntityRequest,
    follow_service: FollowService = Depends(get_follow_service),
    current_user = Depends(get_current_user),
    google_uid: str = Depends(get_google_uid)
):
    """
    Follow an entity (author, institution, topic, or source)
    
    Body:
        - type: "author" | "institution" | "topic" | "source"
        - entityId: OpenAlex entity ID (short form)
        - entityName: Display name
        - openalexId: Full OpenAlex ID
    """
    try:
        if not google_uid or google_uid == 'anonymous':
            raise HTTPException(
                status_code=401,
                detail="Authentication required to follow entities"
            )
        
        # Validate entity type
        if request.type not in ["author", "institution", "topic", "source", "custom"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid entity type: {request.type}. Must be one of: author, institution, topic, source, custom"
            )
        
        # If it's a custom follow, parse the query with GPT
        if request.type == "custom":
            # Get OpenAI API key
            settings = get_settings()
            api_key = settings.openai_api_key
            if not api_key:
                api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise HTTPException(
                    status_code=500,
                    detail="OpenAI API key not configured. Cannot parse custom query."
                )
            
            # Parse the query
            parsed_query = parse_search_query_with_gpt(request.entityName, api_key=api_key)
            
            # Store the parsed query as JSON string in entityId
            request.entityId = json.dumps(parsed_query)
            request.openalexId = request.entityName  # Store original query in openalexId
        
        result = await follow_service.follow_entity(
            user_id=google_uid,
            entity_type=request.type,
            entity_id=request.entityId,
            entity_name=request.entityName,
            openalex_id=request.openalexId
        )
        
        return {"success": True, "follow": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ Error in follow_entity endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error following entity: {str(e)}"
        )


@router.delete("/{entity_type}/{entity_id}")
async def unfollow_entity(
    entity_type: str,
    entity_id: str,
    follow_service: FollowService = Depends(get_follow_service),
    current_user = Depends(get_current_user),
    google_uid: str = Depends(get_google_uid)
):
    """
    Unfollow an entity
    
    Path parameters:
        - entity_type: "author" | "institution" | "topic" | "source"
        - entity_id: OpenAlex entity ID
    """
    try:
        if not google_uid or google_uid == 'anonymous':
            raise HTTPException(
                status_code=401,
                detail="Authentication required to unfollow entities"
            )
        
        # Validate entity type
        if entity_type not in ["author", "institution", "topic", "source", "custom"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid entity type: {entity_type}. Must be one of: author, institution, topic, source, custom"
            )
        
        success = await follow_service.unfollow_entity(
            user_id=google_uid,
            entity_type=entity_type,
            entity_id=entity_id
        )
        
        return {"success": success}
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ Error in unfollow_entity endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error unfollowing entity: {str(e)}"
        )


@router.get("")
async def get_follows(
    follow_service: FollowService = Depends(get_follow_service),
    current_user = Depends(get_current_user),
    google_uid: str = Depends(get_google_uid)
):
    """
    Get all follows for the current user
    
    Returns list of all followed entities grouped by type.
    """
    try:
        if not google_uid or google_uid == 'anonymous':
            return {"follows": []}
        
        follows = await follow_service.get_user_follows(google_uid)
        return {"follows": follows}
    except Exception as e:
        print(f"⚠️ Error in get_follows endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting follows: {str(e)}"
        )


@router.get("/papers")
async def get_followed_papers(
    limit_per_entity: int = 50,
    total_limit: int = 200,
    follow_service: FollowService = Depends(get_follow_service),
    current_user = Depends(get_current_user),
    google_uid: str = Depends(get_google_uid)
):
    """
    Get papers from all followed entities, merged and sorted by recency
    
    Query parameters:
        - limit_per_entity: Maximum papers per followed entity (default: 50)
        - total_limit: Maximum total papers to return (default: 200)
    
    Returns list of papers sorted by publication date (most recent first).
    """
    try:
        if not google_uid or google_uid == 'anonymous':
            return {"papers": [], "count": 0}
        
        print(f"🔍 Fetching followed papers for user: {google_uid}")
        papers = await follow_service.get_followed_papers(
            user_id=google_uid,
            limit_per_entity=limit_per_entity,
            total_limit=total_limit
        )
        
        print(f"✅ Got {len(papers)} papers from followed entities")
        
        # Convert papers to dict format for JSON response
        papers_data = []
        for paper in papers:
            try:
                papers_data.append(paper.model_dump(by_alias=True))
            except Exception as e:
                paper_id = paper.paper_id if hasattr(paper, 'paper_id') else 'unknown'
                print(f"⚠️ Error serializing paper {paper_id}: {e}")
                continue
        
        return {
            "papers": papers_data,
            "count": len(papers_data)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ Error in get_followed_papers endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error getting followed papers: {str(e)}"
        )

