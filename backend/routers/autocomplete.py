"""
Autocomplete API Router

Endpoints for providing autocomplete suggestions from OpenAlex API.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from ..services.openalex_autocomplete import OpenAlexAutocompleteService
from ..dependencies import get_openalex_service


router = APIRouter(prefix="/api/autocomplete", tags=["autocomplete"])


def get_autocomplete_service() -> OpenAlexAutocompleteService:
    """Dependency to get OpenAlex autocomplete service instance"""
    return OpenAlexAutocompleteService()


@router.get("", include_in_schema=True)
async def get_autocomplete(
    q: str = Query(..., description="Search query string (minimum 2 characters)", min_length=2),
    limit: int = Query(10, ge=1, le=20, description="Maximum number of suggestions to return"),
    types: Optional[str] = Query(
        None,
        description="Comma-separated list of types to search (works,authors,sources,institutions,concepts). Default: all types"
    ),
    autocomplete_service: OpenAlexAutocompleteService = Depends(get_autocomplete_service)
):
    """
    Get autocomplete suggestions from OpenAlex API
    
    Provides real-time search suggestions as users type, querying multiple OpenAlex
    endpoints in parallel to suggest papers, authors, journals, institutions, and topics.
    
    **Query Parameters:**
    - `q`: Search query string (required, minimum 2 characters)
    - `limit`: Maximum number of suggestions to return (default: 10, max: 20)
    - `types`: Comma-separated list of types to search (optional)
      - Options: "works", "authors", "sources", "institutions", "concepts"
      - Default: all types
    
    **Returns:**
    ```json
    {
        "suggestions": [
            {
                "text": "Chronic pain research",
                "type": "topic",
                "count": 1250
            },
            {
                "text": "Michael J. Iadarola",
                "type": "author",
                "count": 45
            }
        ]
    }
    ```
    
    **Example:**
    ```
    GET /api/autocomplete?q=chronic pain&limit=5&types=works,authors
    ```
    """
    try:
        # Parse types parameter
        types_list = None
        if types:
            types_list = [t.strip() for t in types.split(",") if t.strip()]
            # Validate types
            valid_types = {"works", "authors", "sources", "institutions", "concepts"}
            invalid_types = set(types_list) - valid_types
            if invalid_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid types: {', '.join(invalid_types)}. Valid types are: {', '.join(valid_types)}"
                )
        
        # Get suggestions from autocomplete service
        suggestions = await autocomplete_service.get_autocomplete_suggestions(
            query=q,
            limit=limit,
            types=types_list
        )
        
        return {
            "suggestions": suggestions
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ Error in autocomplete endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching autocomplete suggestions: {str(e)}"
        )

