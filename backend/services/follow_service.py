"""
Follow Service

Handles following/unfollowing authors, institutions, topics, and sources.
Stores follows in Firebase and fetches papers from followed entities.
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from firebase_admin import firestore

from ..services.firebase_service import FirebaseService
from ..services.openalex_service import OpenAlexService
from ..models.paper import Paper
from ..config import get_settings


class FollowService:
    """Service for managing follows and fetching followed papers"""
    
    def __init__(self, firebase_service: FirebaseService, openalex_service: OpenAlexService):
        self.firebase = firebase_service
        self.openalex = openalex_service
        self.settings = get_settings()
    
    async def follow_entity(
        self,
        user_id: str,
        entity_type: str,
        entity_id: str,
        entity_name: str,
        openalex_id: str
    ) -> Dict[str, Any]:
        """
        Follow an entity (author, institution, topic, or source)
        
        Args:
            user_id: User ID
            entity_type: "author", "institution", "topic", or "source"
            entity_id: OpenAlex entity ID (short form, e.g., "A1234567890")
            entity_name: Display name of the entity
            openalex_id: Full OpenAlex ID (e.g., "https://openalex.org/A1234567890")
        
        Returns:
            Follow document data
        """
        if not self.firebase.db:
            raise Exception("Firebase not initialized")
        
        # Validate entity type
        if entity_type not in ["author", "institution", "topic", "source", "custom"]:
            raise ValueError(f"Invalid entity type: {entity_type}")
        
        # Create follow document ID
        follow_id = f"{user_id}_{entity_type}_{entity_id}"
        
        follow_data = {
            "userId": user_id,
            "type": entity_type,
            "entityId": entity_id,
            "entityName": entity_name,
            "openalexId": openalex_id,
            "followedAt": firestore.SERVER_TIMESTAMP,
            "updatedAt": firestore.SERVER_TIMESTAMP,
        }
        
        # For custom follows, store parsed query data
        if entity_type == "custom":
            # The entity_id should contain the parsed query JSON
            # We'll store it in a separate field for easier access
            follow_data["parsedQuery"] = entity_id  # Store the parsed query JSON string
        
        try:
            follow_ref = self.firebase.db.collection("follows").document(follow_id)
            follow_ref.set(follow_data)
            
            print(f"✅ User {user_id} followed {entity_type}: {entity_name} ({entity_id})")
            
            # Return a serializable version (without Firestore timestamps)
            return {
                "userId": user_id,
                "type": entity_type,
                "entityId": entity_id,
                "entityName": entity_name,
                "openalexId": openalex_id,
                "followedAt": None,  # Will be set by Firestore
                "updatedAt": None,  # Will be set by Firestore
            }
        except Exception as e:
            print(f"⚠️ Error following entity: {e}")
            raise
    
    async def unfollow_entity(
        self,
        user_id: str,
        entity_type: str,
        entity_id: str
    ) -> bool:
        """
        Unfollow an entity
        
        Args:
            user_id: User ID
            entity_type: "author", "institution", "topic", or "source"
            entity_id: OpenAlex entity ID
        
        Returns:
            True if successfully unfollowed
        """
        if not self.firebase.db:
            raise Exception("Firebase not initialized")
        
        follow_id = f"{user_id}_{entity_type}_{entity_id}"
        
        try:
            follow_ref = self.firebase.db.collection("follows").document(follow_id)
            follow_ref.delete()
            
            print(f"✅ User {user_id} unfollowed {entity_type}: {entity_id}")
            return True
        except Exception as e:
            print(f"⚠️ Error unfollowing entity: {e}")
            raise
    
    async def get_user_follows(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all follows for a user
        
        Args:
            user_id: User ID
        
        Returns:
            List of follow documents
        """
        if not self.firebase.db:
            return []
        
        try:
            follows_ref = self.firebase.db.collection("follows")
            query = follows_ref.where("userId", "==", user_id)
            docs = query.stream()
            
            follows = []
            for doc in docs:
                follow_data = doc.to_dict()
                follow_data["id"] = doc.id
                
                # Convert Firestore timestamps to ISO format strings
                if "followedAt" in follow_data and follow_data["followedAt"]:
                    if hasattr(follow_data["followedAt"], "isoformat"):
                        follow_data["followedAt"] = follow_data["followedAt"].isoformat()
                    else:
                        follow_data["followedAt"] = str(follow_data["followedAt"])
                
                if "updatedAt" in follow_data and follow_data["updatedAt"]:
                    if hasattr(follow_data["updatedAt"], "isoformat"):
                        follow_data["updatedAt"] = follow_data["updatedAt"].isoformat()
                    else:
                        follow_data["updatedAt"] = str(follow_data["updatedAt"])
                
                follows.append(follow_data)
            
            return follows
        except Exception as e:
            print(f"⚠️ Error getting user follows: {e}")
            return []
    
    async def _fetch_papers_for_entity(
        self,
        entity_type: str,
        entity_id: str,
        limit: int = 50
    ) -> List[Paper]:
        """
        Fetch papers for a specific entity using OpenAlex API
        
        Args:
            entity_type: "author", "institution", "topic", "source", or "custom"
            entity_id: OpenAlex entity ID (e.g., "A1234567890" or full URL) or parsed query JSON for custom
            limit: Maximum number of papers to fetch
        
        Returns:
            List of Paper objects
        """
        import httpx
        import json
        
        try:
            # Handle custom follows - use parsed query JSON to build OpenAlex API call
            if entity_type == "custom":
                try:
                    # Parse the JSON stored in entity_id
                    parsed_query = json.loads(entity_id)
                    
                    # Extract the parsed entities
                    keywords = parsed_query.get("keywords", []) or []
                    authors = parsed_query.get("authors", []) or []
                    years = parsed_query.get("years", []) or []
                    institutions = parsed_query.get("institutions", []) or []
                    journals = parsed_query.get("journals", []) or []
                    
                    print(f"🔍 Fetching papers for custom query: keywords={keywords}, authors={authors}, years={years}, institutions={institutions}, journals={journals}")
                    
                    # Use OpenAlexService to fetch papers with the parsed query
                    papers = await self.openalex.fetch_papers(
                        topics=keywords,
                        authors=authors,
                        years=years,
                        institutions=institutions,
                        journals=journals,
                        sort_by="recency",
                        page=1,
                        per_page=limit
                    )
                    
                    print(f"✅ Fetched {len(papers)} papers for custom query")
                    return papers
                except json.JSONDecodeError as e:
                    print(f"⚠️ Error parsing custom query JSON: {e}")
                    return []
                except Exception as e:
                    print(f"⚠️ Error fetching papers for custom query: {e}")
                    import traceback
                    traceback.print_exc()
                    return []
            
            # Extract just the ID part if it's a full URL
            if entity_id.startswith("https://openalex.org/"):
                entity_id = entity_id.split("/")[-1]
            elif "/" in entity_id:
                entity_id = entity_id.split("/")[-1]
            
            # Build filter based on entity type
            # OpenAlex filters accept just the ID part (e.g., "A5007856961")
            if entity_type == "author":
                filter_param = f"authorships.author.id:{entity_id}"
            elif entity_type == "institution":
                filter_param = f"authorships.institutions.id:{entity_id}"
            elif entity_type == "topic":
                # Topics are concepts in OpenAlex
                filter_param = f"concepts.id:{entity_id}"
            elif entity_type == "source":
                filter_param = f"primary_location.source.id:{entity_id}"
            else:
                print(f"⚠️ Unknown entity type: {entity_type}")
                return []
            
            print(f"🔍 Fetching papers for {entity_type} {entity_id} with filter: {filter_param}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                params = {
                    "mailto": self.openalex.email,
                    "filter": filter_param,
                    "sort": "publication_date:desc",
                    "per_page": limit,
                    "page": 1,
                    "select": "id,title,abstract_inverted_index,primary_location,doi,publication_year,cited_by_count,authorships",
                }
                
                response = await client.get("https://api.openalex.org/works", params=params)
                response.raise_for_status()
                data = response.json()
                
                papers = []
                for work in data.get("results", []):
                    try:
                        paper = self.openalex._transform_work_to_paper(work)
                        if paper:
                            papers.append(paper)
                    except Exception as e:
                        print(f"⚠️ Error transforming work to paper: {e}")
                        continue
                
                print(f"✅ Fetched {len(papers)} papers for {entity_type} {entity_id}")
                return papers
        except httpx.HTTPError as e:
            print(f"⚠️ HTTP error fetching papers for {entity_type} {entity_id}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   Response status: {e.response.status_code}")
                print(f"   Response text: {e.response.text[:200]}")
            return []
        except Exception as e:
            print(f"⚠️ Error fetching papers for {entity_type} {entity_id}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def get_followed_papers(
        self,
        user_id: str,
        limit_per_entity: int = 50,
        total_limit: int = 200
    ) -> List[Paper]:
        """
        Get papers from all followed entities, merged and sorted by recency
        
        Args:
            user_id: User ID
            limit_per_entity: Maximum papers to fetch per followed entity
            total_limit: Maximum total papers to return
        
        Returns:
            List of papers sorted by publication date (most recent first)
        """
        # Get all user's follows
        follows = await self.get_user_follows(user_id)
        
        if not follows:
            return []
        
        # Group follows by type
        author_follows = [f for f in follows if f.get("type") == "author"]
        institution_follows = [f for f in follows if f.get("type") == "institution"]
        topic_follows = [f for f in follows if f.get("type") == "topic"]
        source_follows = [f for f in follows if f.get("type") == "source"]
        custom_follows = [f for f in follows if f.get("type") == "custom"]
        
        # Create tasks for parallel fetching
        tasks = []
        
        # Fetch papers for all follows (including custom)
        all_follows = author_follows + institution_follows + topic_follows + source_follows + custom_follows
        for follow in all_follows:
            entity_type = follow.get("type")
            entity_id = follow.get("entityId")
            if entity_type and entity_id:
                tasks.append(self._fetch_papers_for_entity(entity_type, entity_id, limit_per_entity))
        
        # Execute all fetches in parallel
        print(f"🔍 Fetching papers from {len(tasks)} followed entities in parallel...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten and collect all papers
        all_papers = []
        for result in results:
            if isinstance(result, Exception):
                print(f"⚠️ Error fetching papers: {result}")
                continue
            if isinstance(result, list):
                all_papers.extend(result)
        
        # Deduplicate by paper ID
        seen_ids = set()
        unique_papers = []
        for paper in all_papers:
            # Paper model uses paper_id, not paperId
            paper_id = paper.paper_id if hasattr(paper, 'paper_id') else getattr(paper, 'paperId', None)
            if paper_id and paper_id not in seen_ids:
                seen_ids.add(paper_id)
                unique_papers.append(paper)
        
        # Sort by publication date (most recent first)
        # Papers without dates go to the end
        unique_papers.sort(
            key=lambda p: (
                p.year if p.year else 0,
                p.paper_id  # Stable sort for papers without year
            ),
            reverse=True
        )
        
        # Limit total results
        return unique_papers[:total_limit]

