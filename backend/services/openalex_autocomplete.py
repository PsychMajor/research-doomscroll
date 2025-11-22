"""
OpenAlex Autocomplete Service

Handles autocomplete suggestions from OpenAlex API for papers, authors, journals, institutions, and topics.
"""

import httpx
import asyncio
from typing import List, Dict, Any, Optional
from ..config import get_settings


class OpenAlexAutocompleteService:
    """Service for fetching autocomplete suggestions from OpenAlex API"""
    
    WORKS_URL = "https://api.openalex.org/works"
    AUTHORS_URL = "https://api.openalex.org/authors"
    SOURCES_URL = "https://api.openalex.org/sources"
    INSTITUTIONS_URL = "https://api.openalex.org/institutions"
    CONCEPTS_URL = "https://api.openalex.org/concepts"
    
    def __init__(self):
        self.settings = get_settings()
        self.email = self.settings.openalex_email
    
    async def _fetch_suggestions(
        self,
        client: httpx.AsyncClient,
        url: str,
        query: str,
        limit: int = 5,
        select_fields: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch suggestions from a specific OpenAlex endpoint
        
        Args:
            client: HTTP client instance
            url: OpenAlex API endpoint URL
            query: Search query string
            limit: Maximum number of suggestions to return
            select_fields: Fields to select in response
        
        Returns:
            List of suggestion dictionaries
        """
        try:
            params = {
                "mailto": self.email,
                "search": query,
                "per_page": limit,
            }
            
            if select_fields:
                params["select"] = ",".join(select_fields)
            
            response = await client.get(url, params=params, timeout=5.0)
            response.raise_for_status()
            data = response.json()
            
            return data.get("results", [])
        except Exception as e:
            print(f"⚠️ Error fetching suggestions from {url}: {e}")
            return []
    
    async def get_autocomplete_suggestions(
        self,
        query: str,
        limit: int = 5,
        types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get autocomplete suggestions from multiple OpenAlex endpoints in parallel
        
        Args:
            query: Search query string
            limit: Maximum number of suggestions per type (default: 5)
            types: List of types to search (None = all types)
                   Options: "works", "authors", "sources", "institutions", "concepts"
        
        Returns:
            List of suggestion dictionaries with structure:
            {
                "text": str,  # Display text
                "type": str,  # "paper", "author", "journal", "institution", "topic"
                "count": int  # Optional count/score
            }
        """
        if not query or len(query.strip()) < 2:
            return []
        
        query = query.strip()
        
        # Default to all types if not specified
        if types is None:
            types = ["works", "authors", "sources", "institutions", "concepts"]
        
        suggestions = []
        
        # Query all endpoints in parallel
        async with httpx.AsyncClient() as client:
            tasks = []
            task_types = []  # Track which type each task corresponds to
            
            # Works (papers) suggestions
            if "works" in types:
                tasks.append(
                    self._fetch_suggestions(
                        client,
                        self.WORKS_URL,
                        query,
                        limit,
                        ["id", "title", "cited_by_count"]
                    )
                )
                task_types.append("works")
            
            # Authors suggestions
            if "authors" in types:
                tasks.append(
                    self._fetch_suggestions(
                        client,
                        self.AUTHORS_URL,
                        query,
                        limit,
                        ["id", "display_name", "works_count"]
                    )
                )
                task_types.append("authors")
            
            # Sources (journals) suggestions
            if "sources" in types:
                tasks.append(
                    self._fetch_suggestions(
                        client,
                        self.SOURCES_URL,
                        query,
                        limit,
                        ["id", "display_name", "works_count"]
                    )
                )
                task_types.append("sources")
            
            # Institutions suggestions
            if "institutions" in types:
                tasks.append(
                    self._fetch_suggestions(
                        client,
                        self.INSTITUTIONS_URL,
                        query,
                        limit,
                        ["id", "display_name", "works_count"]
                    )
                )
                task_types.append("institutions")
            
            # Concepts (topics) suggestions
            if "concepts" in types:
                tasks.append(
                    self._fetch_suggestions(
                        client,
                        self.CONCEPTS_URL,
                        query,
                        limit,
                        ["id", "display_name", "works_count"]
                    )
                )
                task_types.append("concepts")
            
            # Execute all queries in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results based on task_types mapping
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    continue
                
                task_type = task_types[i] if i < len(task_types) else None
                
                if task_type == "works":
                    for work in result:
                        suggestions.append({
                            "text": work.get("title", ""),
                            "type": "paper",
                            "count": work.get("cited_by_count", 0)
                        })
                elif task_type == "authors":
                    for author in result:
                        suggestions.append({
                            "text": author.get("display_name", ""),
                            "type": "author",
                            "count": author.get("works_count", 0)
                        })
                elif task_type == "sources":
                    for source in result:
                        suggestions.append({
                            "text": source.get("display_name", ""),
                            "type": "journal",
                            "count": source.get("works_count", 0)
                        })
                elif task_type == "institutions":
                    for institution in result:
                        suggestions.append({
                            "text": institution.get("display_name", ""),
                            "type": "institution",
                            "count": institution.get("works_count", 0)
                        })
                elif task_type == "concepts":
                    for concept in result:
                        suggestions.append({
                            "text": concept.get("display_name", ""),
                            "type": "topic",
                            "count": concept.get("works_count", 0)
                        })
        
        # Deduplicate suggestions by text and type
        seen = set()
        deduplicated = []
        for suggestion in suggestions:
            key = (suggestion["text"].lower(), suggestion["type"])
            if key not in seen and suggestion["text"]:
                seen.add(key)
                deduplicated.append(suggestion)
        
        # Sort by relevance (exact match first, then by count)
        query_lower = query.lower()
        deduplicated.sort(
            key=lambda x: (
                0 if x["text"].lower().startswith(query_lower) else 1,  # Starts-with first
                -x.get("count", 0)  # Higher count first
            )
        )
        
        # Limit total suggestions to exactly the requested limit
        return deduplicated[:limit]

