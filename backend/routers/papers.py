"""
Papers API Router

Endpoints for searching and retrieving academic papers from OpenAlex.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from ..models.paper import Paper
from ..services.openalex_service import OpenAlexService
from ..services.database_service import DatabaseService
from ..dependencies import get_openalex_service, get_db_service, get_current_user


router = APIRouter(prefix="/api/papers", tags=["papers"])


@router.get("/search", response_model=List[Paper])
async def search_papers(
    topics: Optional[str] = Query(None, description="Comma-separated topic keywords"),
    authors: Optional[str] = Query(None, description="Comma-separated author names"),
    sort_by: str = Query("recency", description="Sort by 'recency' or 'relevance'"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    per_page: int = Query(200, ge=1, le=200, description="Results per page (max 200)"),
    openalex: OpenAlexService = Depends(get_openalex_service),
    db: DatabaseService = Depends(get_db_service),
    current_user = Depends(get_current_user)
):
    """
    Search papers via OpenAlex API
    
    This endpoint searches for academic papers using the OpenAlex API.
    Results are cached in the database for faster subsequent retrievals.
    
    **Query Parameters:**
    - `topics`: Comma-separated keywords to search in title/abstract (e.g., "machine learning, neural networks")
    - `authors`: Comma-separated author names (e.g., "John Smith, Jane Doe")
    - `sort_by`: Sort order - "recency" (newest first) or "relevance" (most cited)
    - `page`: Page number for pagination (starts at 1)
    - `per_page`: Number of results per page (max 200)
    
    **Returns:**
    List of Paper objects with metadata including:
    - Title, abstract, authors
    - Publication year, venue, citation count
    - TL;DR summary (auto-generated)
    - OpenAlex ID and URL
    
    **Example:**
    ```
    GET /api/papers/search?topics=quantum+computing&authors=John+Preskill&sort_by=recency&page=1
    ```
    """
    # Parse comma-separated inputs
    topics_list = [t.strip() for t in topics.split(",")] if topics else []
    authors_list = [a.strip() for a in authors.split(",")] if authors else []
    
    # Validate that at least one search criterion is provided
    if not topics_list and not authors_list:
        raise HTTPException(
            status_code=400,
            detail="At least one of 'topics' or 'authors' must be provided"
        )
    
    # Validate sort_by parameter
    if sort_by not in ["recency", "relevance"]:
        raise HTTPException(
            status_code=400,
            detail="sort_by must be either 'recency' or 'relevance'"
        )
    
    try:
        # Fetch papers from OpenAlex
        papers = await openalex.fetch_papers(
            topics=topics_list,
            authors=authors_list,
            sort_by=sort_by,
            page=page,
            per_page=per_page
        )
        
        # Cache papers in database for future retrieval
        if papers:
            await db.cache_papers(papers)
        
        return papers
        
    except Exception as e:
        print(f"❌ Error searching papers: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error searching papers: {str(e)}"
        )


@router.get("/{paper_id}", response_model=Paper)
async def get_paper(
    paper_id: str,
    openalex: OpenAlexService = Depends(get_openalex_service),
    db: DatabaseService = Depends(get_db_service),
    current_user = Depends(get_current_user)
):
    """
    Get a specific paper by ID
    
    Retrieves a single paper by its OpenAlex ID. First checks the database cache,
    then fetches from OpenAlex API if not found locally.
    
    **Path Parameters:**
    - `paper_id`: OpenAlex work ID (e.g., "W2104477830")
    
    **Returns:**
    Paper object with full metadata
    
    **Example:**
    ```
    GET /api/papers/W2104477830
    ```
    """
    try:
        # Try to get paper from database cache first
        paper = await db.get_paper(paper_id)
        
        if not paper:
            # Not in cache, fetch from OpenAlex API
            print(f"📥 Paper {paper_id} not in cache, fetching from OpenAlex...")
            paper = await openalex.fetch_paper_by_id(paper_id)
            
            if not paper:
                raise HTTPException(
                    status_code=404,
                    detail=f"Paper with ID '{paper_id}' not found"
                )
            
            # Cache the fetched paper
            await db.cache_papers([paper])
        else:
            print(f"✅ Paper {paper_id} retrieved from cache")
        
        return paper
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting paper: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving paper: {str(e)}"
        )


@router.get("/bulk/by-ids", response_model=List[Paper])
async def get_papers_by_ids(
    paper_ids: str = Query(..., description="Comma-separated paper IDs"),
    db: DatabaseService = Depends(get_db_service),
    current_user = Depends(get_current_user)
):
    """
    Get multiple papers by their IDs
    
    Retrieves multiple papers from the database cache by their OpenAlex IDs.
    Useful for fetching papers in folders or liked papers.
    
    **Query Parameters:**
    - `paper_ids`: Comma-separated OpenAlex IDs (e.g., "W123,W456,W789")
    
    **Returns:**
    List of Paper objects (only those found in database)
    
    **Example:**
    ```
    GET /api/papers/bulk/by-ids?paper_ids=W2104477830,W2964141474
    ```
    """
    try:
        # Parse comma-separated IDs
        ids_list = [pid.strip() for pid in paper_ids.split(",") if pid.strip()]
        
        if not ids_list:
            raise HTTPException(
                status_code=400,
                detail="At least one paper ID must be provided"
            )
        
        # Get papers from database
        papers = await db.get_papers_by_ids(ids_list)
        
        return papers
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting papers by IDs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving papers: {str(e)}"
        )
