"""
Entity Search API Router

Endpoints for searching authors, institutions, topics, and sources in OpenAlex.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List
from ..services.entity_search_service import EntitySearchService
from ..dependencies import get_current_user


router = APIRouter(prefix="/api/entity-search", tags=["entity-search"])


def get_entity_search_service() -> EntitySearchService:
    """Dependency to get entity search service instance"""
    return EntitySearchService()


@router.get("/authors")
async def search_authors(
    q: str = Query(..., description="Search query string", min_length=1),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    entity_search_service: EntitySearchService = Depends(get_entity_search_service),
    current_user = Depends(get_current_user)
):
    """
    Search for authors in OpenAlex
    
    Returns list of authors matching the search query.
    """
    try:
        results = await entity_search_service.search_authors(q, limit)
        return {"results": results}
    except Exception as e:
        print(f"⚠️ Error in search_authors endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error searching authors: {str(e)}"
        )


@router.get("/institutions")
async def search_institutions(
    q: str = Query(..., description="Search query string", min_length=1),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    entity_search_service: EntitySearchService = Depends(get_entity_search_service),
    current_user = Depends(get_current_user)
):
    """
    Search for institutions in OpenAlex
    
    Returns list of institutions matching the search query.
    """
    try:
        results = await entity_search_service.search_institutions(q, limit)
        return {"results": results}
    except Exception as e:
        print(f"⚠️ Error in search_institutions endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error searching institutions: {str(e)}"
        )


@router.get("/topics")
async def search_topics(
    q: str = Query(..., description="Search query string", min_length=1),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    entity_search_service: EntitySearchService = Depends(get_entity_search_service),
    current_user = Depends(get_current_user)
):
    """
    Search for topics/concepts in OpenAlex
    
    Returns list of topics matching the search query.
    """
    try:
        results = await entity_search_service.search_topics(q, limit)
        return {"results": results}
    except Exception as e:
        print(f"⚠️ Error in search_topics endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error searching topics: {str(e)}"
        )


@router.get("/sources")
async def search_sources(
    q: str = Query(..., description="Search query string", min_length=1),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results"),
    entity_search_service: EntitySearchService = Depends(get_entity_search_service),
    current_user = Depends(get_current_user)
):
    """
    Search for sources/journals in OpenAlex
    
    Returns list of sources matching the search query.
    """
    try:
        results = await entity_search_service.search_sources(q, limit)
        return {"results": results}
    except Exception as e:
        print(f"⚠️ Error in search_sources endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error searching sources: {str(e)}"
        )

