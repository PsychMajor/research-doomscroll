"""
Papers API Router

Endpoints for searching and retrieving academic papers from OpenAlex.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
import os
from ..models.paper import Paper
from ..services.openalex_service import OpenAlexService
from ..services.database_service import DatabaseService
from ..dependencies import get_openalex_service, get_db_service, get_current_user, require_user_id


router = APIRouter(prefix="/api/papers", tags=["papers"])


@router.get("/recommendations", response_model=List[Paper])
async def get_recommendations(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of recommendations to return"),
    user_id: int = Depends(require_user_id),
    openalex: OpenAlexService = Depends(get_openalex_service),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Get personalized paper recommendations
    
    Provides personalized recommendations based on:
    - User's saved profile (topics and authors)
    - User's liked papers (similar papers to liked ones)
    - Recent papers in user's areas of interest
    
    **Query Parameters:**
    - `limit`: Maximum number of recommendations to return (default: 20, max: 100)
    
    **Returns:**
    List of Paper objects recommended for the user
    
    **Example:**
    ```
    GET /api/papers/recommendations?limit=20
    ```
    """
    try:
        # Load user's profile
        profile = await db.load_profile(user_id=user_id)
        topics = profile.topics
        authors = profile.authors
        
        # Load user's liked papers
        feedback = await db.load_feedback(user_id=user_id)
        liked_paper_ids = feedback.liked
        
        papers = []
        
        # Strategy 1: Fetch papers based on user's profile topics/authors
        if topics or authors:
            print(f"💡 Fetching recommendations based on profile: topics={topics}, authors={authors}")
            profile_papers = await openalex.fetch_papers(
                topics=topics,
                authors=authors,
                sort_by="relevance",  # Use relevance for recommendations
                page=1,
                per_page=min(limit, 200)
            )
            papers.extend(profile_papers)
            print(f"   ✅ Found {len(profile_papers)} papers from profile")
        
        # Strategy 2: Get similar papers to user's liked papers
        if liked_paper_ids and len(papers) < limit:
            print(f"💡 Fetching similar papers to {len(liked_paper_ids)} liked papers")
            remaining_limit = limit - len(papers)
            papers_per_liked = max(1, remaining_limit // len(liked_paper_ids))
            
            for liked_id in liked_paper_ids[:5]:  # Limit to first 5 liked papers to avoid too many API calls
                if len(papers) >= limit:
                    break
                
                similar = await openalex.fetch_related_works(
                    liked_id,
                    limit=min(papers_per_liked, limit - len(papers))
                )
                papers.extend(similar)
                print(f"   ✅ Found {len(similar)} similar papers to {liked_id}")
        
        # Remove duplicates (by paper_id)
        seen_ids = set()
        unique_papers = []
        for paper in papers:
            if paper.paper_id not in seen_ids:
                seen_ids.add(paper.paper_id)
                unique_papers.append(paper)
            if len(unique_papers) >= limit:
                break
        
        # Cache papers in database
        if unique_papers:
            await db.cache_papers(unique_papers)
        
        print(f"✅ Returning {len(unique_papers)} recommendations")
        return unique_papers[:limit]
        
    except Exception as e:
        print(f"❌ Error fetching recommendations: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching recommendations: {str(e)}"
        )


@router.get("/search/query", response_model=List[Paper])
async def search_papers_by_query(
    q: str = Query(..., description="Natural language search query (e.g., 'machine learning by John Smith' or 'quantum computing papers')"),
    sort_by: str = Query("recency", description="Sort by 'recency' or 'relevance'"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    per_page: int = Query(200, ge=1, le=200, description="Results per page (max 200)"),
    openalex: OpenAlexService = Depends(get_openalex_service),
    db: DatabaseService = Depends(get_db_service),
    current_user = Depends(get_current_user)
):
    """
    Search papers via OpenAlex API using natural language query
    
    This endpoint parses a natural language query to extract keywords and authors,
    then searches for academic papers using the OpenAlex API.
    Results are cached in the database for faster subsequent retrievals.
    
    **Query Parameters:**
    - `q`: Natural language search query that will be parsed for keywords and authors
      - Examples:
        - "machine learning by John Smith"
        - "John Smith, Jane Doe neural networks"
        - "quantum computing papers"
        - "pain research by Michael J. Iadarola"
        - "machine learning, deep learning by John Smith and Jane Doe"
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
    GET /api/papers/search/query?q=machine+learning+by+John+Smith&sort_by=recency&page=1
    ```
    """
    from ..utils.gpt_query_parser import parse_search_query_with_gpt
    from ..config import get_settings
    
    # Parse the query to extract keywords, authors, years, and institutions
    settings = get_settings()
    # Try to get API key from settings first, then environment, then .env file directly
    api_key = settings.openai_api_key
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Try reading from .env file directly as fallback
        from pathlib import Path
        env_file = Path(__file__).parent.parent.parent / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("OPENAI_API_KEY="):
                    api_key = line.split("=", 1)[1]
                    break
    
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured. Please set OPENAI_API_KEY in .env file."
        )
    
    parsed = parse_search_query_with_gpt(q, api_key=api_key)
    
    # Extract parsed entities from JSON response
    topics_list = parsed.get("keywords", []) or []
    authors_list = parsed.get("authors", []) or []
    years_list = parsed.get("years", []) or []
    institutions_list = parsed.get("institutions", []) or []
    journals_list = parsed.get("journals", []) or []
    
    # Log the parsed results for debugging
    print(f"🔍 GPT parsed query '{q}' -> JSON: {parsed}")
    print(f"   Extracted: keywords={topics_list}, authors={authors_list}, years={years_list}, institutions={institutions_list}, journals={journals_list}")
    
    # Validate that at least one search criterion was extracted
    if not topics_list and not authors_list and not years_list and not institutions_list and not journals_list:
        raise HTTPException(
            status_code=400,
            detail="Could not extract keywords, authors, years, institutions, or journals from query. Please try a different format."
        )
    
    # Validate sort_by parameter
    if sort_by not in ["recency", "relevance"]:
        raise HTTPException(
            status_code=400,
            detail="sort_by must be either 'recency' or 'relevance'"
        )
    
    try:
        # Step 1: Make initial API call with original keywords (not expanded)
        print(f"🔍 Making initial API call with original keywords: {topics_list}")
        papers = await openalex.fetch_papers(
            topics=topics_list,
            authors=authors_list,
            years=years_list,
            institutions=institutions_list,
            journals=journals_list,
            sort_by=sort_by,
            page=page,
            per_page=per_page
        )
        
        print(f"   ✅ Initial search returned {len(papers)} papers")
        
        # Step 2: Check if we need to expand (only if < 50 papers and we have keywords to expand)
        if len(papers) < 50 and topics_list:
            print(f"   ⚠️  Less than 50 papers found, expanding search with related keywords...")
            
            # Expand keywords to get related terms
            from ..utils.keyword_expansion import expand_keywords
            expanded_keywords = expand_keywords(topics_list, api_key=api_key, max_expansions=5)
            
            # Filter out original keywords to get only new expanded ones
            new_keywords = [kw for kw in expanded_keywords if kw not in topics_list]
            
            if new_keywords:
                # Use the first expanded keyword for additional search
                expanded_keyword = new_keywords[0]
                print(f"   🔍 Making additional API call with expanded keyword: '{expanded_keyword}'")
                
                # Make additional API call with one expanded keyword
                expanded_papers = await openalex.fetch_papers(
                    topics=[expanded_keyword],
                    authors=authors_list,
                    years=years_list,
                    institutions=institutions_list,
                    journals=journals_list,
                    sort_by=sort_by,
                    page=page,
                    per_page=per_page
                )
                
                print(f"   ✅ Expanded search returned {len(expanded_papers)} papers")
                
                # Keep original results first, then append expanded results (deduplicated)
                # Don't re-sort - maintain order: original first, then expanded
                seen_paper_ids = {paper.paper_id for paper in papers}
                original_count = len(papers)
                
                # Append expanded papers that aren't duplicates
                for paper in expanded_papers:
                    if paper.paper_id not in seen_paper_ids:
                        papers.append(paper)
                        seen_paper_ids.add(paper.paper_id)
                
                expanded_count = len(papers) - original_count
                print(f"   ✅ Combined results: {original_count} original + {expanded_count} expanded = {len(papers)} unique papers total")
                print(f"   📋 Order: Original results first, then expanded results")
                
                # Limit to per_page results (original first, then expanded)
                papers = papers[:per_page]
            else:
                print(f"   ⚠️  No new expanded keywords generated, using original results")
        else:
            if len(papers) >= 50:
                print(f"   ✅ Sufficient results ({len(papers)} papers), no expansion needed")
            elif not topics_list:
                print(f"   ⚠️  No keywords to expand, using original results")
        
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


@router.get("/{paper_id}/similar", response_model=List[Paper])
async def get_similar_papers(
    paper_id: str,
    limit: int = Query(10, ge=1, le=50, description="Maximum number of similar papers to return"),
    openalex: OpenAlexService = Depends(get_openalex_service),
    db: DatabaseService = Depends(get_db_service),
    current_user = Depends(get_current_user)
):
    """
    Get papers similar to the given paper
    
    Retrieves related works from OpenAlex based on the paper's citation network
    and semantic similarity. Results are cached in the database.
    
    **Path Parameters:**
    - `paper_id`: OpenAlex work ID (e.g., "W2104477830")
    
    **Query Parameters:**
    - `limit`: Maximum number of similar papers to return (default: 10, max: 50)
    
    **Returns:**
    List of Paper objects that are similar to the given paper
    
    **Example:**
    ```
    GET /api/papers/W2104477830/similar?limit=10
    ```
    """
    try:
        # Fetch related works from OpenAlex
        papers = await openalex.fetch_related_works(paper_id, limit=limit)
        
        # Cache papers in database for future retrieval
        if papers:
            await db.cache_papers(papers)
        
        return papers
        
    except Exception as e:
        print(f"❌ Error fetching similar papers: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching similar papers: {str(e)}"
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
