"""
OpenAlex API Service

Handles all interactions with the OpenAlex API for fetching academic papers
and author information.
"""

import httpx
from typing import List, Optional, Dict, Any
from ..models.paper import Paper, Author
from ..config import get_settings


class OpenAlexService:
    """Service for interacting with OpenAlex API"""
    
    BASE_URL = "https://api.openalex.org/works"
    AUTHORS_URL = "https://api.openalex.org/authors"
    
    def __init__(self):
        self.settings = get_settings()
        self.email = self.settings.openalex_email
    
    async def fetch_papers(
        self,
        topics: List[str] = [],
        authors: List[str] = [],
        years: List[str] = [],
        institutions: List[str] = [],
        sort_by: str = "recency",
        page: int = 1,
        per_page: int = 200
    ) -> List[Paper]:
        """
        Fetch papers from OpenAlex API
        
        Args:
            topics: List of topic keywords
            authors: List of author names
            years: List of year filters (e.g., ["2020"], ["2020-2023"], [">2020"], ["<2023"])
            institutions: List of institution names
            sort_by: Sort order - "relevance" (citations) or "recency" (newest first)
            page: Page number
            per_page: Number of results per page (max 200)
        
        Returns:
            List of Paper models
        """
        # Determine sort parameter
        sort_param = "publication_date:desc" if sort_by == "recency" else "cited_by_count:desc"
        
        # Build request parameters
        params = {
            "mailto": self.email,
            "per_page": per_page,
            "page": page,
            "sort": sort_param,
            "select": "id,title,abstract_inverted_index,primary_location,doi,publication_year,cited_by_count,authorships",
        }
        
        # Build filters
        filters = []
        
        # Get author IDs if authors are provided
        author_ids = []
        if authors:
            print(f"🔍 Looking up author IDs for {len(authors)} author(s): {authors}")
            author_ids = await self._get_author_ids(authors)
            if author_ids:
                print(f"   ✅ Found {len(author_ids)} author ID(s): {author_ids}")
            else:
                print(f"   ⚠️ No author IDs found, will search by name instead")
        
        # Strategy: Use search parameter if no author filters, otherwise use only filters
        if author_ids:
            # We have author IDs, so we use filter parameter
            if len(author_ids) == 1:
                filters.append(f"authorships.author.id:{author_ids[0]}")
            else:
                # Multiple authors - use OR syntax with pipe
                author_ids_str = "|".join(author_ids)
                filters.append(f"authorships.author.id:{author_ids_str}")
            
            # Add topic search using default.search filter
            if topics:
                topic_query = " ".join(topics)
                filters.append(f"default.search:{topic_query}")
        else:
            # No author filters, use search parameter
            if topics:
                topic_query = " ".join(topics)
                params["search"] = topic_query
            
            # Fallback: if we have author names but couldn't get IDs
            if authors and not author_ids:
                if not topics:
                    params["search"] = " ".join(authors)
                else:
                    params["search"] = params["search"] + " " + " ".join(authors)
        
        # Add year filters
        if years:
            year_filters = []
            for year in years:
                if "-" in year and not year.startswith(">") and not year.startswith("<"):
                    # Range: "2020-2023" -> publication_year:2020-2023
                    filters.append(f"publication_year:{year}")
                elif year.startswith(">"):
                    # After: ">2020" -> publication_year:>2020
                    year_val = year[1:]
                    filters.append(f"publication_year:>{year_val}")
                elif year.startswith("<"):
                    # Before: "<2023" -> publication_year:<2023
                    year_val = year[1:]
                    filters.append(f"publication_year:<{year_val}")
                else:
                    # Single year: "2020" -> publication_year:2020
                    # For multiple single years, we'll combine them with OR
                    year_filters.append(year)
            
            # If we have multiple single years, combine them with OR
            if len(year_filters) > 1:
                year_filter_str = "|".join(year_filters)
                filters.append(f"publication_year:{year_filter_str}")
            elif len(year_filters) == 1:
                filters.append(f"publication_year:{year_filters[0]}")
        
        # Add institution filters
        if institutions:
            # For institutions, we'll search by display name since looking up IDs is complex
            # OpenAlex supports: institutions.display_name.search:MIT
            inst_filters = []
            for inst in institutions:
                # Clean institution name
                inst_clean = inst.strip()
                if inst_clean:
                    inst_filters.append(f'institutions.display_name.search:"{inst_clean}"')
            
            if inst_filters:
                # For multiple institutions, use OR (pipe)
                if len(inst_filters) == 1:
                    filters.append(inst_filters[0])
                else:
                    # Combine institution names with OR
                    inst_names = [f.split('"')[1] for f in inst_filters]
                    inst_filter_str = "|".join(inst_names)
                    filters.append(f'institutions.display_name.search:"{inst_filter_str}"')
        
        # Add filters to params (comma means AND in OpenAlex)
        if filters:
            params["filter"] = ",".join(filters)
        
        try:
            print(f"🔍 Fetching from OpenAlex: page={page}, topics={topics}, authors={authors}, years={years}, institutions={institutions}, sort={sort_by}")
            print(f"   Search: {params.get('search', 'N/A')}")
            print(f"   Filter: {params.get('filter', 'N/A')}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
            
            raw_results = data.get("results", [])
            print(f"   📊 OpenAlex returned {len(raw_results)} raw results")
            
            papers = []
            for i, work in enumerate(raw_results):
                if not work or not work.get("id"):
                    print(f"   ⚠️ Skipping work {i}: missing id")
                    continue
                
                paper = self._transform_work_to_paper(work)
                if paper:
                    papers.append(paper)
                else:
                    print(f"   ⚠️ Transformation failed for work {i}: {work.get('id', 'unknown')}")
            
            print(f"✅ Fetched {len(papers)} papers from OpenAlex (transformed from {len(raw_results)} raw results)")
            return papers
            
        except httpx.HTTPError as e:
            print(f"❌ OpenAlex API error: {e}")
            return []
        except Exception as e:
            print(f"❌ Error processing OpenAlex data: {e}")
            return []
    
    async def fetch_paper_by_id(self, paper_id: str) -> Optional[Paper]:
        """
        Fetch a single paper from OpenAlex by its ID
        
        Args:
            paper_id: OpenAlex paper ID (e.g., "W2104477830")
        
        Returns:
            Paper model or None if not found
        """
        try:
            # Clean the ID - extract just the W... part if it's a URL
            if paper_id.startswith('http'):
                paper_id = paper_id.split('/')[-1]
            
            # Ensure it starts with W
            if not paper_id.startswith('W'):
                paper_id = f"W{paper_id}"
            
            url = f"{self.BASE_URL}/{paper_id}"
            params = {"mailto": self.email} if self.email else {}
            
            print(f"🔍 Fetching paper from OpenAlex: {paper_id}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                work = response.json()
            
            paper = self._transform_work_to_paper(work)
            return paper
            
        except httpx.HTTPError as e:
            print(f"❌ OpenAlex API error: {e}")
            return None
        except Exception as e:
            print(f"❌ Error processing OpenAlex paper: {e}")
            return None
    
    async def fetch_related_works(self, paper_id: str, limit: int = 10) -> List[Paper]:
        """
        Fetch related works for a paper from OpenAlex
        
        OpenAlex provides related works in the work object itself via the
        'related_works' field which contains URLs to related papers.
        
        Args:
            paper_id: OpenAlex paper ID (e.g., "W2104477830")
            limit: Maximum number of related papers to return
        
        Returns:
            List of Paper models for related works
        """
        try:
            # Clean the ID - extract just the W... part if it's a URL
            if paper_id.startswith('http'):
                paper_id = paper_id.split('/')[-1]
            
            # Ensure it starts with W
            if not paper_id.startswith('W'):
                paper_id = f"W{paper_id}"
            
            url = f"{self.BASE_URL}/{paper_id}"
            params = {
                "mailto": self.email,
                "select": "id,related_works"  # Only fetch what we need
            }
            
            print(f"🔗 Fetching related works for paper: {paper_id}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                work = response.json()
            
            # Get related work IDs from the related_works field
            related_work_urls = work.get("related_works", [])
            if not related_work_urls:
                print(f"   ℹ️  No related works found for {paper_id}")
                return []
            
            # Extract IDs from URLs (format: https://openalex.org/W1234567890)
            related_ids = []
            for url in related_work_urls[:limit]:
                if isinstance(url, str) and '/W' in url:
                    work_id = url.split('/')[-1]
                    if work_id.startswith('W'):
                        related_ids.append(work_id)
            
            if not related_ids:
                print(f"   ℹ️  Could not extract related work IDs")
                return []
            
            print(f"   ✅ Found {len(related_ids)} related work IDs, fetching details...")
            
            # Fetch full details for each related work
            papers = []
            async with httpx.AsyncClient(timeout=30.0) as client:
                for work_id in related_ids:
                    try:
                        work_url = f"{self.BASE_URL}/{work_id}"
                        work_params = {
                            "mailto": self.email,
                            "select": "id,title,abstract_inverted_index,primary_location,doi,publication_year,cited_by_count,authorships"
                        }
                        
                        work_response = await client.get(work_url, params=work_params)
                        work_response.raise_for_status()
                        related_work = work_response.json()
                        
                        paper = self._transform_work_to_paper(related_work)
                        if paper:
                            papers.append(paper)
                    except Exception as e:
                        print(f"   ⚠️  Error fetching related work {work_id}: {e}")
                        continue
            
            print(f"✅ Fetched {len(papers)} related papers")
            return papers
            
        except httpx.HTTPError as e:
            print(f"❌ OpenAlex API error fetching related works: {e}")
            return []
        except Exception as e:
            print(f"❌ Error fetching related works: {e}")
            return []
    
    async def _get_author_ids(self, author_names: List[str]) -> List[str]:
        """
        Query OpenAlex authors endpoint to get author IDs from names
        
        Args:
            author_names: List of author names to search for
        
        Returns:
            List of OpenAlex author IDs
        """
        author_ids = []
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for name in author_names:
                try:
                    params = {
                        "mailto": self.email,
                        "search": name,
                        "per_page": 1  # Just get the top match
                    }
                    
                    response = await client.get(self.AUTHORS_URL, params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    results = data.get("results", [])
                    if results:
                        # Get the OpenAlex ID (format: https://openalex.org/A1234567890)
                        author_id = results[0].get("id", "")
                        if author_id:
                            # Extract just the ID part (A1234567890)
                            author_id = author_id.split("/")[-1]
                            author_ids.append(author_id)
                            print(f"   Found author: {results[0].get('display_name')} -> {author_id}")
                except Exception as e:
                    print(f"   ⚠️ Could not find author ID for '{name}': {e}")
        
        return author_ids
    
    def _transform_work_to_paper(self, work: Dict[str, Any]) -> Optional[Paper]:
        """
        Transform OpenAlex work data to Paper model
        
        Args:
            work: Raw OpenAlex work data
        
        Returns:
            Paper model or None if transformation fails
        """
        try:
            from ..utils.text_processing import format_scientific_text, summarize_text
            
            # Extract paper ID
            paper_id = work.get("id", "").split("/")[-1]
            if not paper_id:
                return None
            
            # Extract and format title
            title = format_scientific_text(work.get("title") or "Untitled")
            
            # Convert inverted index to abstract text
            abstract_text = None
            if work.get("abstract_inverted_index") and isinstance(work["abstract_inverted_index"], dict):
                try:
                    inverted = work["abstract_inverted_index"]
                    word_positions = []
                    for word, positions in inverted.items():
                        if positions:
                            for pos in positions:
                                word_positions.append((pos, word))
                    
                    if word_positions:
                        word_positions.sort(key=lambda x: x[0])
                        abstract_text = " ".join([word for _, word in word_positions])
                        abstract_text = format_scientific_text(abstract_text)
                except Exception as e:
                    print(f"⚠️  Error reconstructing abstract: {e}")
            
            # Extract authors
            authors = []
            for authorship in work.get("authorships", [])[:10]:  # Limit to first 10 authors
                if not authorship:
                    continue
                author_info = authorship.get("author") or {}
                if author_info.get("display_name"):
                    authors.append(Author(
                        name=author_info.get("display_name"),
                        id=author_info.get("id", "").split("/")[-1] if author_info.get("id") else None
                    ))
            
            # Extract venue/journal
            venue = None
            primary_location = work.get("primary_location") or {}
            if isinstance(primary_location, dict):
                source = primary_location.get("source") or {}
                if isinstance(source, dict) and source.get("display_name"):
                    venue = source.get("display_name")
            
            # Get URL
            url = None
            if isinstance(primary_location, dict):
                url = primary_location.get("landing_page_url")
            if not url:
                url = work.get("doi")
            
            # Generate TL;DR
            tldr = summarize_text(abstract_text, sentences_count=2) if abstract_text else None
            
            # Create Paper model
            paper = Paper(
                paperId=paper_id,
                title=title,
                abstract=abstract_text,
                authors=authors,
                year=work.get("publication_year"),
                venue=venue,
                citationCount=work.get("cited_by_count", 0),
                url=url,
                tldr=tldr,
                source="openalex"
            )
            
            return paper
            
        except Exception as e:
            print(f"❌ Error transforming work to paper: {e}")
            return None
