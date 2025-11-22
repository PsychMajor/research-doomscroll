"""
Entity Search Service

Handles searching for authors, institutions, topics, and sources in OpenAlex API.
"""

import httpx
from typing import List, Dict, Any, Optional
from ..config import get_settings


class EntitySearchService:
    """Service for searching entities in OpenAlex API"""
    
    AUTHORS_URL = "https://api.openalex.org/authors"
    INSTITUTIONS_URL = "https://api.openalex.org/institutions"
    CONCEPTS_URL = "https://api.openalex.org/concepts"
    SOURCES_URL = "https://api.openalex.org/sources"
    
    def __init__(self):
        self.settings = get_settings()
        self.email = self.settings.openalex_email
    
    async def search_authors(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for authors in OpenAlex
        
        Args:
            query: Search query string
            limit: Maximum number of results
        
        Returns:
            List of author dictionaries with id, display_name, works_count, etc.
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {
                    "mailto": self.email,
                    "search": query,
                    "per_page": limit,
                    "select": "id,display_name,works_count,orcid"
                }
                
                response = await client.get(self.AUTHORS_URL, params=params)
                response.raise_for_status()
                data = response.json()
                
                results = data.get("results", [])
                return [
                    {
                        "id": author.get("id", "").split("/")[-1] if author.get("id") else "",
                        "openalexId": author.get("id", ""),
                        "name": author.get("display_name", ""),
                        "worksCount": author.get("works_count", 0),
                        "orcid": author.get("orcid", ""),
                    }
                    for author in results
                ]
        except Exception as e:
            print(f"⚠️ Error searching authors: {e}")
            return []
    
    async def search_institutions(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for institutions in OpenAlex
        
        Args:
            query: Search query string
            limit: Maximum number of results
        
        Returns:
            List of institution dictionaries
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {
                    "mailto": self.email,
                    "search": query,
                    "per_page": limit,
                    "select": "id,display_name,works_count,country_code"
                }
                
                response = await client.get(self.INSTITUTIONS_URL, params=params)
                response.raise_for_status()
                data = response.json()
                
                results = data.get("results", [])
                return [
                    {
                        "id": inst.get("id", "").split("/")[-1] if inst.get("id") else "",
                        "openalexId": inst.get("id", ""),
                        "name": inst.get("display_name", ""),
                        "worksCount": inst.get("works_count", 0),
                        "countryCode": inst.get("country_code", ""),
                    }
                    for inst in results
                ]
        except Exception as e:
            print(f"⚠️ Error searching institutions: {e}")
            return []
    
    async def search_topics(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for topics/concepts in OpenAlex
        
        Args:
            query: Search query string
            limit: Maximum number of results
        
        Returns:
            List of topic/concept dictionaries
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {
                    "mailto": self.email,
                    "search": query,
                    "per_page": limit,
                    "select": "id,display_name,works_count,level"
                }
                
                response = await client.get(self.CONCEPTS_URL, params=params)
                response.raise_for_status()
                data = response.json()
                
                results = data.get("results", [])
                return [
                    {
                        "id": concept.get("id", "").split("/")[-1] if concept.get("id") else "",
                        "openalexId": concept.get("id", ""),
                        "name": concept.get("display_name", ""),
                        "worksCount": concept.get("works_count", 0),
                        "level": concept.get("level", 0),
                    }
                    for concept in results
                ]
        except Exception as e:
            print(f"⚠️ Error searching topics: {e}")
            return []
    
    async def search_sources(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for sources/journals in OpenAlex
        
        Args:
            query: Search query string
            limit: Maximum number of results
        
        Returns:
            List of source/journal dictionaries
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {
                    "mailto": self.email,
                    "search": query,
                    "per_page": limit,
                    "select": "id,display_name,works_count,issn"
                }
                
                response = await client.get(self.SOURCES_URL, params=params)
                response.raise_for_status()
                data = response.json()
                
                results = data.get("results", [])
                return [
                    {
                        "id": source.get("id", "").split("/")[-1] if source.get("id") else "",
                        "openalexId": source.get("id", ""),
                        "name": source.get("display_name", ""),
                        "worksCount": source.get("works_count", 0),
                        "issn": source.get("issn", []),
                    }
                    for source in results
                ]
        except Exception as e:
            print(f"⚠️ Error searching sources: {e}")
            return []

