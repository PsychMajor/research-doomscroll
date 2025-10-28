from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import os
import json
from pathlib import Path

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Hard-coded interests
INTERESTS = "dopamine addiction nucleus accumbens"

# Semantic Scholar search endpoint
SEMANTIC_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

# bioRxiv API endpoint
BIORXIV_URL = "https://api.biorxiv.org/details/biorxiv"

# Optional API key from environment variable
API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")

# Profile storage
PROFILE_FILE = Path("profile.json")
FEEDBACK_FILE = Path("feedback.json")

# Paper cache for load-more functionality
# Structure: {cache_key: {"semantic_scholar": [...], "biorxiv": [...], "mixed": [...]}}
PAPER_CACHE = {}

# Download NLTK data on startup
try:
    import nltk
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

def generate_tldr(abstract):
    """Generate a TLDR summary from an abstract using extractive summarization"""
    if not abstract or len(abstract.strip()) < 50:
        return None
    
    try:
        from sumy.parsers.plaintext import PlaintextParser
        from sumy.nlp.tokenizers import Tokenizer
        from sumy.summarizers.lsa import LsaSummarizer
        from sumy.nlp.stemmers import Stemmer
        from sumy.utils import get_stop_words
        
        # Parse the abstract
        parser = PlaintextParser.from_string(abstract, Tokenizer("english"))
        stemmer = Stemmer("english")
        summarizer = LsaSummarizer(stemmer)
        summarizer.stop_words = get_stop_words("english")
        
        # Get 1 sentence summary
        summary = summarizer(parser.document, 1)
        
        if summary:
            return str(summary[0])
        return None
    except Exception as e:
        print(f"Error generating TLDR: {e}")
        return None

def load_profile():
    """Load user profile from file"""
    if PROFILE_FILE.exists():
        with open(PROFILE_FILE, 'r') as f:
            return json.load(f)
    return {"topics": [], "authors": []}

def save_profile(topics_list, authors_list):
    """Save user profile to file"""
    profile = {
        "topics": topics_list,
        "authors": authors_list
    }
    with open(PROFILE_FILE, 'w') as f:
        json.dump(profile, f, indent=2)
    return profile

def load_feedback():
    """Load user feedback (likes/dislikes) from file"""
    if FEEDBACK_FILE.exists():
        with open(FEEDBACK_FILE, 'r') as f:
            return json.load(f)
    return {"liked": [], "disliked": []}

def save_feedback(feedback_data):
    """Save user feedback to file"""
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(feedback_data, f, indent=2)
    return feedback_data

def get_paper_id_from_url(url):
    """Extract paper ID from Semantic Scholar URL"""
    if not url:
        return None
    # URL format: https://www.semanticscholar.org/paper/{paper_id}
    parts = url.rstrip('/').split('/')
    return parts[-1] if parts else None

async def fetch_biorxiv_papers(query_terms, max_results=20, quick_mode=False):
    """Fetch papers from bioRxiv API - only fetches cursor=0 (first 100 papers) from each day
    
    Args:
        query_terms: Search terms
        max_results: Maximum number of papers to return
        quick_mode: If True, only search recent days for faster initial results
    """
    import asyncio
    import aiohttp
    from datetime import datetime, timedelta
    
    try:
        print(f"Searching bioRxiv for terms: {query_terms}")
        
        # Shared counter for progress reporting
        match_counter = {"count": 0, "lock": asyncio.Lock()}
        
        # Split into days for parallelization
        now = datetime.now()
        date_ranges = []
        
        # In quick mode, only search last 10 days for faster response
        num_days = 10 if quick_mode else 30
        
        for i in range(num_days):
            day = now - timedelta(days=i)
            # Each range is a single day
            date_str = day.strftime("%Y-%m-%d")
            date_ranges.append((date_str, date_str))
        
        print(f"Fetching bioRxiv papers from {len(date_ranges)} days in parallel (cursor=0 only)")
        if quick_mode:
            print("⚡ Quick mode: Searching recent days only for faster results")
        
        async def fetch_date_range(session, start_date, end_date, semaphore):
            """Fetch only cursor=0 for a specific date"""
            range_papers = []
            cursor = 0  # Only fetch first page
            
            async with semaphore:  # Limit concurrent requests
                url = f"{BIORXIV_URL}/{start_date}/{end_date}/{cursor}"
                try:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                        if response.status != 200:
                            print(f"bioRxiv returned {response.status} for {start_date} to {end_date}")
                            return range_papers
                        
                        data = await response.json()
                        
                        if "collection" not in data or not data["collection"]:
                            return range_papers
                        
                        batch = data["collection"]
                        print(f"Got {len(batch)} papers from {start_date} (cursor=0)")
                        
                        # Filter papers by query terms
                        local_matches = 0
                        for paper_data in batch:
                            title = paper_data.get("title", "").lower()
                            abstract = paper_data.get("abstract", "").lower()
                            
                            # Check if any query term matches
                            matches = False
                            for term in query_terms.split(","):
                                term_clean = term.strip().lower()
                                if term_clean and (term_clean in title or term_clean in abstract):
                                    matches = True
                                    break
                            
                            if matches:
                                local_matches += 1
                                
                                # Extract author names
                                authors = []
                                if paper_data.get("authors"):
                                    author_str = paper_data.get("authors", "")
                                    author_names = author_str.split(";")
                                    authors = [{"name": name.strip()} for name in author_names if name.strip()]
                                
                                # Create paper ID from DOI
                                doi = paper_data.get("doi", "")
                                paper_id = f"biorxiv_{doi.replace('/', '_')}"
                                
                                # Generate TLDR from abstract
                                abstract_text = paper_data.get("abstract", "No abstract available")
                                tldr_text = generate_tldr(abstract_text) if abstract_text != "No abstract available" else None
                                
                                paper = {
                                    "paperId": paper_id,
                                    "title": paper_data.get("title", "No title"),
                                    "abstract": abstract_text,
                                    "tldr": tldr_text,
                                    "url": f"https://www.biorxiv.org/content/{doi}v{paper_data.get('version', '1')}",
                                    "authors": authors,
                                    "year": paper_data.get("date", "N/A")[:4],
                                    "citationCount": 0,
                                    "venue": None,  # bioRxiv papers don't have journal info
                                    "source": "bioRxiv"
                                }
                                range_papers.append(paper)
                        
                        # Update counter and report progress every 5 matches
                        async with match_counter["lock"]:
                            old_count = match_counter["count"]
                            match_counter["count"] += local_matches
                            new_count = match_counter["count"]
                            
                            # Report every 5 papers
                            old_milestone = old_count // 5
                            new_milestone = new_count // 5
                            
                            if new_milestone > old_milestone:
                                print(f"🔍 Progress: {new_count} matching papers found so far...")
                        
                except asyncio.TimeoutError:
                    print(f"Timeout fetching {start_date} to {end_date}")
                except Exception as e:
                    print(f"Error fetching {start_date} to {end_date}: {e}")
            
            return range_papers
        
        # Fetch all date ranges in parallel with concurrency limit
        semaphore = asyncio.Semaphore(10)  # Limit to 10 concurrent requests
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_date_range(session, start, end, semaphore) for start, end in date_ranges]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results from all date ranges
        all_papers = []
        for result in results:
            if isinstance(result, list):
                all_papers.extend(result)
            else:
                print(f"Error in parallel fetch: {result}")
        
        # Remove duplicates (by paperId) and limit to max_results
        seen_ids = set()
        unique_papers = []
        for paper in all_papers:
            if paper["paperId"] not in seen_ids:
                seen_ids.add(paper["paperId"])
                unique_papers.append(paper)
                if len(unique_papers) >= max_results:
                    break
        
        print(f"Found {len(unique_papers)} matching bioRxiv papers (from {len(all_papers)} total)")
        return unique_papers
    
    except Exception as e:
        print(f"bioRxiv API error: {e}")
        import traceback
        traceback.print_exc()
        return []

@app.get("/", response_class=HTMLResponse)
async def get_paper(request: Request, topics: str = "", authors: str = "", use_recommendations: bool = False):
    # Load saved profile and feedback
    profile = load_profile()
    feedback = load_feedback()
    
    # If no search parameters provided, check if we have a saved profile
    if not topics and not authors:
        if profile["topics"] or profile["authors"]:
            # Use saved profile to generate feed
            topics = ", ".join(profile["topics"])
            authors = ", ".join(profile["authors"])
        else:
            # Show the search form for first-time users
            return templates.TemplateResponse("index.html", {
                "request": request, 
                "papers": [],
                "show_form": True,
                "topics": "",
                "authors": "",
                "profile": profile,
                "feedback": feedback
            })
    
    # Check if we should use recommendations instead of search
    if use_recommendations and feedback["liked"]:
        # Use Semantic Scholar recommendations API
        try:
            # Get recommendations based on liked papers
            positive_ids = feedback["liked"][-10:]  # Use last 10 liked papers
            
            headers = {}
            if API_KEY:
                headers["x-api-key"] = API_KEY
            
            # Get recommendations for each liked paper and combine
            all_recommendations = []
            for paper_id in positive_ids[:3]:  # Limit to avoid rate limits
                rec_url = f"https://api.semanticscholar.org/recommendations/v1/papers/forpaper/{paper_id}"
                params = {
                    "fields": "title,abstract,url,authors,year,citationCount,tldr,venue,publicationVenue",
                    "limit": 10
                }
                rec_response = requests.get(rec_url, params=params, headers=headers, timeout=10)
                
                if rec_response.status_code == 200:
                    rec_data = rec_response.json()
                    if "recommendedPapers" in rec_data:
                        all_recommendations.extend(rec_data["recommendedPapers"])
            
            # Remove duplicates and already rated papers
            seen_ids = set(feedback["liked"] + feedback["disliked"])
            unique_papers = []
            seen_titles = set()
            
            for paper_data in all_recommendations:
                paper_id = paper_data.get("paperId")
                title = paper_data.get("title", "")
                
                if paper_id not in seen_ids and title not in seen_titles:
                    unique_papers.append(paper_data)
                    seen_titles.add(title)
                    if len(unique_papers) >= 20:
                        break
            
            papers = []
            for paper_data in unique_papers:
                # Extract TLDR if available
                tldr_text = None
                if paper_data.get("tldr") and paper_data["tldr"].get("text"):
                    tldr_text = paper_data["tldr"]["text"]
                
                # Extract venue/journal information
                venue = None
                if paper_data.get("publicationVenue") and paper_data["publicationVenue"].get("name"):
                    venue = paper_data["publicationVenue"]["name"]
                elif paper_data.get("venue"):
                    venue = paper_data["venue"]
                
                paper = {
                    "paperId": paper_data.get("paperId"),
                    "title": paper_data.get("title", "No title"),
                    "abstract": paper_data.get("abstract", "No abstract available"),
                    "tldr": tldr_text,
                    "url": paper_data.get("url", ""),
                    "authors": paper_data.get("authors", []),
                    "year": paper_data.get("year", "N/A"),
                    "citationCount": paper_data.get("citationCount", 0),
                    "venue": venue,
                    "source": "Semantic Scholar"
                }
                papers.append(paper)
            
            return templates.TemplateResponse("index.html", {
                "request": request, 
                "papers": papers,
                "show_form": True,
                "topics": topics,
                "authors": authors,
                "profile": profile,
                "feedback": feedback,
                "using_recommendations": True
            })
            
        except Exception as e:
            # Fall back to regular search if recommendations fail
            pass
    
    # Build search query
    query_parts = []
    if topics:
        query_parts.append(topics)
    if authors:
        # Add author filter to the query
        author_list = [a.strip() for a in authors.split(',')]
        for author in author_list:
            query_parts.append(f'author:"{author}"')
    
    search_query = " ".join(query_parts) if query_parts else INTERESTS
    
    # Get already rated paper IDs to filter them out
    rated_paper_ids = set(feedback["liked"] + feedback["disliked"])
    
    params = {
        "query": search_query,
        "limit": 100,  # Fetch more papers so we can filter and still get 20
        "fields": "paperId,title,abstract,url,authors,year,citationCount,tldr,venue,publicationVenue"
    }

    headers = {}
    if API_KEY:
        headers["x-api-key"] = API_KEY

    papers = []
    semantic_error = None
    
    # Try to fetch from Semantic Scholar
    try:
        response = requests.get(SEMANTIC_URL, params=params, headers=headers, timeout=10)
        data = response.json()

        # Check for API errors
        if response.status_code == 429:
            semantic_error = "⏰ Semantic Scholar rate limit reached, showing bioRxiv papers only."
        elif response.status_code != 200:
            semantic_error = f"Semantic Scholar API Error: {data.get('message', 'Unknown error')}"
        else:
            # Extract papers from Semantic Scholar
            if "data" in data and len(data["data"]) > 0:
                for paper_data in data["data"]:
                    paper_id = paper_data.get("paperId")
                    
                    # Skip papers that have already been rated
                    if paper_id in rated_paper_ids:
                        continue
                    
                    # Collect ALL filtered papers, don't stop at 20
                    # We want to cache extras for "Load More"
                    
                    # Extract TLDR if available
                    tldr_text = None
                    if paper_data.get("tldr") and paper_data["tldr"].get("text"):
                        tldr_text = paper_data["tldr"]["text"]
                    
                    # Extract venue/journal information
                    venue = None
                    if paper_data.get("publicationVenue") and paper_data["publicationVenue"].get("name"):
                        venue = paper_data["publicationVenue"]["name"]
                    elif paper_data.get("venue"):
                        venue = paper_data["venue"]
                    
                    paper = {
                        "paperId": paper_id,
                        "title": paper_data.get("title", "No title"),
                        "abstract": paper_data.get("abstract", "No abstract available"),
                        "tldr": tldr_text,
                        "url": paper_data.get("url", ""),
                        "authors": paper_data.get("authors", []),
                        "year": paper_data.get("year", "N/A"),
                        "citationCount": paper_data.get("citationCount", 0),
                        "venue": venue,
                        "source": "Semantic Scholar"
                    }
                    papers.append(paper)
    
    except requests.exceptions.RequestException as e:
        semantic_error = f"Semantic Scholar connection error, showing bioRxiv papers only."
    
    # Always try to fetch from bioRxiv (regardless of Semantic Scholar status)
    # For quick initial display: first do a quick search of recent papers
    if topics and len(papers) < 5:
        print(f"⚡ Quick fetch: Getting recent bioRxiv papers for fast display...")
        quick_biorxiv_papers = await fetch_biorxiv_papers(topics, max_results=20, quick_mode=True)
        
        # Filter out already rated papers
        for paper in quick_biorxiv_papers:
            if paper["paperId"] not in rated_paper_ids:
                papers.append(paper)
        
        print(f"⚡ Quick fetch complete: {len(papers)} papers ready to display")
    
    # If we have at least 5 papers, we can return immediately for fast display
    # Then continue fetching more in the background for caching
    if len(papers) >= 5 and topics:
        import random
        import asyncio
        random.shuffle(papers)
        
        # Display first 5-20 papers immediately
        displayed_papers = papers[:min(20, len(papers))]
        
        print(f"🚀 FAST DISPLAY: Showing {len(displayed_papers)} papers immediately")
        print(f"=" * 60)
        print(f"📄 LOADING {len(displayed_papers)} CARDS ON PAGE")
        print(f"   - Semantic Scholar: {sum(1 for p in displayed_papers if p['source'] == 'Semantic Scholar')}")
        print(f"   - bioRxiv: {sum(1 for p in displayed_papers if p['source'] == 'bioRxiv')}")
        print(f"=" * 60)
        
        # Cache the rest from quick fetch
        if len(papers) > len(displayed_papers):
            cached_papers = papers[len(displayed_papers):]
            semantic_papers_cache = [p for p in cached_papers if p['source'] == 'Semantic Scholar']
            biorxiv_papers_cache = [p for p in cached_papers if p['source'] == 'bioRxiv']
            
            cache_key = f"{topics}_{authors}_{use_recommendations}"
            PAPER_CACHE[cache_key] = {
                "semantic_scholar": semantic_papers_cache,
                "biorxiv": biorxiv_papers_cache,
                "mixed": cached_papers
            }
            print(f"📦 Cached {len(cached_papers)} papers from quick fetch")
        
        # Start background task to fetch full 30 days and update cache
        async def background_fetch():
            try:
                print(f"🔄 Background: Starting full 30-day fetch for caching...")
                full_biorxiv_papers = await fetch_biorxiv_papers(topics, max_results=100, quick_mode=False)
                
                # Filter out already rated papers
                filtered_full = []
                for paper in full_biorxiv_papers:
                    if paper["paperId"] not in rated_paper_ids:
                        filtered_full.append(paper)
                
                print(f"🔄 Background: Got {len(filtered_full)} papers from full 30-day search")
                
                # Combine with existing papers and remove duplicates
                seen_ids = set(p["paperId"] for p in papers)
                additional_papers = []
                for paper in filtered_full:
                    if paper["paperId"] not in seen_ids:
                        additional_papers.append(paper)
                        seen_ids.add(paper["paperId"])
                
                if additional_papers:
                    print(f"🔄 Background: Found {len(additional_papers)} NEW papers from extended search")
                    
                    # Update cache with all papers (old + new)
                    all_papers = papers + additional_papers
                    random.shuffle(all_papers)
                    
                    # Remove the ones already displayed
                    displayed_ids = set(p["paperId"] for p in displayed_papers)
                    cacheable_papers = [p for p in all_papers if p["paperId"] not in displayed_ids]
                    
                    semantic_papers_cache = [p for p in cacheable_papers if p['source'] == 'Semantic Scholar']
                    biorxiv_papers_cache = [p for p in cacheable_papers if p['source'] == 'bioRxiv']
                    
                    cache_key = f"{topics}_{authors}_{use_recommendations}"
                    PAPER_CACHE[cache_key] = {
                        "semantic_scholar": semantic_papers_cache,
                        "biorxiv": biorxiv_papers_cache,
                        "mixed": cacheable_papers
                    }
                    print(f"📦 Background: Updated cache with {len(cacheable_papers)} total papers")
                    print(f"   📚 Semantic Scholar: {len(semantic_papers_cache)} papers")
                    print(f"   🧬 bioRxiv: {len(biorxiv_papers_cache)} papers")
                else:
                    print(f"🔄 Background: No new papers found in extended search")
                    
            except Exception as e:
                print(f"❌ Background fetch error: {e}")
        
        # Schedule background task without waiting for it
        asyncio.create_task(background_fetch())
        print(f"🔄 Background fetch scheduled (will continue after response)")
        
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "papers": displayed_papers,
            "show_form": True,
            "topics": topics,
            "authors": authors,
            "profile": profile,
            "feedback": feedback,
            "info_message": semantic_error
        })
    
    # Otherwise, do a full fetch if we don't have enough papers yet
    if topics and len(papers) < 20:
        print(f"Fetching bioRxiv papers for topics: {topics}")
        # Fetch many more papers to have extras for caching (fetch up to 100 from bioRxiv)
        fetch_limit = 100
        biorxiv_papers = await fetch_biorxiv_papers(topics, max_results=fetch_limit, quick_mode=False)
        
        # Filter out already rated papers - but DON'T limit here, collect them all
        filtered_biorxiv = []
        for paper in biorxiv_papers:
            if paper["paperId"] not in rated_paper_ids:
                filtered_biorxiv.append(paper)
        
        print(f"Got {len(filtered_biorxiv)} bioRxiv papers (filtered from {len(biorxiv_papers)})")
        papers.extend(filtered_biorxiv)
    
    print(f"Total papers fetched: {len(papers)}")
    
    # If we have no papers at all, show error
    if not papers:
        error_message = semantic_error if semantic_error else "No papers found for your search."
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "papers": [], 
            "error": error_message,
            "show_form": True,
            "topics": topics,
            "authors": authors,
            "profile": profile,
            "feedback": feedback
        })
    
    # Shuffle all papers before splitting
    import random
    random.shuffle(papers)
    
    # Store extra papers in cache for load-more functionality
    displayed_papers = papers[:20]  # First 20 for display
    if len(papers) > 20:
        cached_papers = papers[20:]
        
        # Separate by source
        semantic_papers = [p for p in cached_papers if p['source'] == 'Semantic Scholar']
        biorxiv_papers = [p for p in cached_papers if p['source'] == 'bioRxiv']
        
        # Create a cache key based on search parameters
        cache_key = f"{topics}_{authors}_{use_recommendations}"
        PAPER_CACHE[cache_key] = {
            "semantic_scholar": semantic_papers,
            "biorxiv": biorxiv_papers,
            "mixed": cached_papers  # Keep shuffled version for mixed loading
        }
        
        print(f"📦 Cached {len(cached_papers)} extra papers for load-more")
        print(f"   📚 Semantic Scholar: {len(semantic_papers)} papers")
        print(f"   🧬 bioRxiv: {len(biorxiv_papers)} papers")
        print(f"📦 Cache key: '{cache_key}'")
        print(f"📦 Total cache entries: {len(PAPER_CACHE)}")
    
    print(f"Displaying first {len(displayed_papers)} papers")
    
    # Log the number of papers being displayed
    print(f"=" * 60)
    print(f"📄 LOADING {len(displayed_papers)} CARDS ON PAGE")
    print(f"   - Semantic Scholar: {sum(1 for p in displayed_papers if p['source'] == 'Semantic Scholar')}")
    print(f"   - bioRxiv: {sum(1 for p in displayed_papers if p['source'] == 'bioRxiv')}")
    print(f"   - Filtered out {len(rated_paper_ids)} already-rated papers")
    print(f"=" * 60)
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "papers": displayed_papers,
        "show_form": True,
        "topics": topics,
        "authors": authors,
        "profile": profile,
        "feedback": feedback,
        "info_message": semantic_error  # Show info if Semantic Scholar failed but we have bioRxiv papers
    })

@app.get("/api/papers")
def get_papers_api():
    """API endpoint to get papers as JSON"""
    params = {
        "query": INTERESTS,
        "limit": 10,
        "fields": "title,abstract,url,authors,year,citationCount"
    }

    response = requests.get(SEMANTIC_URL, params=params)
    data = response.json()

    return data

@app.get("/api/load-more")
async def load_more_papers_api(topics: str = "", authors: str = "", use_recommendations: bool = False):
    """API endpoint to load more papers without page reload"""
    feedback = load_feedback()
    rated_paper_ids = set(feedback["liked"] + feedback["disliked"])
    
    # Create cache key
    cache_key = f"{topics}_{authors}_{use_recommendations}"
    
    print(f"🔍 LOAD MORE: Looking for cache key: '{cache_key}'")
    print(f"🔍 Available cache keys: {list(PAPER_CACHE.keys())}")
    print(f"🔍 Total cache entries: {len(PAPER_CACHE)}")
    
    # Check if we have cached papers first
    if cache_key in PAPER_CACHE and PAPER_CACHE[cache_key].get("mixed"):
        cache_data = PAPER_CACHE[cache_key]
        mixed_papers = cache_data["mixed"]
        
        print(f"📦 LOAD MORE: Found cache with:")
        print(f"   📚 Semantic Scholar: {len(cache_data['semantic_scholar'])} papers")
        print(f"   🧬 bioRxiv: {len(cache_data['biorxiv'])} papers")
        print(f"   🔀 Mixed: {len(mixed_papers)} papers")
        
        # Get up to 20 papers from mixed cache
        cached_papers = mixed_papers[:20]
        remaining_mixed = mixed_papers[20:]
        
        # Filter out any papers that have been rated since caching
        fresh_papers = [p for p in cached_papers if p["paperId"] not in rated_paper_ids]
        
        # Update cache - also update the source-specific caches
        semantic_remaining = [p for p in cache_data["semantic_scholar"] if p["paperId"] not in [fp["paperId"] for fp in cached_papers]]
        biorxiv_remaining = [p for p in cache_data["biorxiv"] if p["paperId"] not in [fp["paperId"] for fp in cached_papers]]
        
        PAPER_CACHE[cache_key] = {
            "semantic_scholar": semantic_remaining,
            "biorxiv": biorxiv_remaining,
            "mixed": remaining_mixed
        }
        
        print(f"📦 LOAD MORE: Serving {len(fresh_papers)} papers from cache")
        print(f"   📚 Semantic Scholar in batch: {sum(1 for p in fresh_papers if p['source'] == 'Semantic Scholar')}")
        print(f"   🧬 bioRxiv in batch: {sum(1 for p in fresh_papers if p['source'] == 'bioRxiv')}")
        print(f"📦 CACHE STATUS: {len(remaining_mixed)} papers remaining")
        print(f"   📚 Semantic Scholar remaining: {len(semantic_remaining)}")
        print(f"   🧬 bioRxiv remaining: {len(biorxiv_remaining)}")
        
        # If we have enough cached papers, return them
        if len(fresh_papers) >= 10:  # Minimum threshold
            return {"papers": fresh_papers, "count": len(fresh_papers), "from_cache": True}
        else:
            # Not enough cached papers, fetch new ones
            print(f"⚠️  Cache depleted ({len(fresh_papers)} papers not enough), fetching fresh papers...")
            papers = fresh_papers  # Start with what we have from cache
    else:
        papers = []
        cache_status = "empty" if cache_key in PAPER_CACHE else "not initialized"
        print(f"🔄 LOAD MORE: No cached papers available (cache {cache_status}), fetching new papers from APIs")
    
    # Build search query
    query_parts = []
    if topics:
        query_parts.append(topics)
    if authors:
        author_list = [a.strip() for a in authors.split(',')]
        for author in author_list:
            query_parts.append(f'author:"{author}"')
    
    search_query = " ".join(query_parts) if query_parts else INTERESTS
    
    params = {
        "query": search_query,
        "limit": 100,
        "fields": "paperId,title,abstract,url,authors,year,citationCount,tldr,venue,publicationVenue"
    }

    headers = {}
    if API_KEY:
        headers["x-api-key"] = API_KEY

    # Fetch from Semantic Scholar
    try:
        response = requests.get(SEMANTIC_URL, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                for paper_data in data["data"]:
                    paper_id = paper_data.get("paperId")
                    
                    if paper_id in rated_paper_ids:
                        continue
                    
                    if len(papers) >= 20:
                        break
                    
                    tldr_text = None
                    if paper_data.get("tldr") and paper_data["tldr"].get("text"):
                        tldr_text = paper_data["tldr"]["text"]
                    
                    venue = None
                    if paper_data.get("publicationVenue") and paper_data["publicationVenue"].get("name"):
                        venue = paper_data["publicationVenue"]["name"]
                    elif paper_data.get("venue"):
                        venue = paper_data["venue"]
                    
                    paper = {
                        "paperId": paper_id,
                        "title": paper_data.get("title", "No title"),
                        "abstract": paper_data.get("abstract", "No abstract available"),
                        "tldr": tldr_text,
                        "url": paper_data.get("url", ""),
                        "authors": paper_data.get("authors", []),
                        "year": paper_data.get("year", "N/A"),
                        "citationCount": paper_data.get("citationCount", 0),
                        "venue": venue,
                        "source": "Semantic Scholar"
                    }
                    papers.append(paper)
    except Exception as e:
        print(f"Error fetching from Semantic Scholar: {e}")
    
    # Fetch from bioRxiv if needed
    papers_needed = 20 - len(papers)
    if topics and papers_needed > 0:
        fetch_limit = max(papers_needed * 3, 60)
        biorxiv_papers = await fetch_biorxiv_papers(topics, max_results=fetch_limit)
        
        filtered_biorxiv = []
        for paper in biorxiv_papers:
            if paper["paperId"] not in rated_paper_ids:
                filtered_biorxiv.append(paper)
                if len(filtered_biorxiv) >= papers_needed:
                    break
        
        papers.extend(filtered_biorxiv)
    
    # Shuffle papers
    import random
    random.shuffle(papers)
    
    return {"papers": papers, "count": len(papers), "from_cache": False}

@app.post("/profile/save")
async def save_profile_endpoint(topics: str = Form(""), authors: str = Form("")):
    """Save user profile"""
    topics_list = [t.strip() for t in topics.split(',') if t.strip()]
    authors_list = [a.strip() for a in authors.split(',') if a.strip()]
    
    save_profile(topics_list, authors_list)
    
    # Redirect to home with the saved interests
    if topics or authors:
        return RedirectResponse(url=f"/?topics={topics}&authors={authors}", status_code=303)
    return RedirectResponse(url="/", status_code=303)

@app.get("/profile")
async def get_profile():
    """Get current profile as JSON"""
    return load_profile()

@app.post("/profile/clear")
async def clear_profile():
    """Clear saved profile"""
    save_profile([], [])
    return RedirectResponse(url="/", status_code=303)

@app.post("/paper/like")
async def like_paper(paper_id: str = Form(...)):
    """Like a paper - add to positive feedback"""
    feedback = load_feedback()
    
    # Remove from disliked if present
    if paper_id in feedback["disliked"]:
        feedback["disliked"].remove(paper_id)
    
    # Add to liked if not already there
    if paper_id not in feedback["liked"]:
        feedback["liked"].append(paper_id)
    
    save_feedback(feedback)
    return {"status": "success", "action": "liked", "paper_id": paper_id}

@app.post("/paper/unlike")
async def unlike_paper(paper_id: str = Form(...)):
    """Unlike a paper - remove from positive feedback"""
    feedback = load_feedback()
    
    # Remove from liked if present
    if paper_id in feedback["liked"]:
        feedback["liked"].remove(paper_id)
    
    save_feedback(feedback)
    return {"status": "success", "action": "unliked", "paper_id": paper_id}

@app.post("/paper/dislike")
async def dislike_paper(paper_id: str = Form(...)):
    """Dislike a paper - add to negative feedback"""
    feedback = load_feedback()
    
    # Remove from liked if present
    if paper_id in feedback["liked"]:
        feedback["liked"].remove(paper_id)
    
    # Add to disliked if not already there
    if paper_id not in feedback["disliked"]:
        feedback["disliked"].append(paper_id)
    
    save_feedback(feedback)
    return {"status": "success", "action": "disliked", "paper_id": paper_id}

@app.post("/paper/undislike")
async def undislike_paper(paper_id: str = Form(...)):
    """Undislike a paper - remove from negative feedback"""
    feedback = load_feedback()
    
    # Remove from disliked if present
    if paper_id in feedback["disliked"]:
        feedback["disliked"].remove(paper_id)
    
    save_feedback(feedback)
    return {"status": "success", "action": "undisliked", "paper_id": paper_id}

@app.get("/feedback")
async def get_feedback():
    """Get current feedback statistics"""
    feedback = load_feedback()
    return {
        "liked_count": len(feedback["liked"]),
        "disliked_count": len(feedback["disliked"]),
        "liked": feedback["liked"],
        "disliked": feedback["disliked"]
    }

@app.post("/feedback/clear")
async def clear_feedback():
    """Clear all feedback"""
    save_feedback({"liked": [], "disliked": []})
    return RedirectResponse(url="/", status_code=303)

@app.post("/feedback/clear/liked")
async def clear_liked():
    """Clear only liked papers"""
    feedback = load_feedback()
    feedback["liked"] = []
    save_feedback(feedback)
    return RedirectResponse(url="/", status_code=303)

@app.post("/feedback/clear/disliked")
async def clear_disliked():
    """Clear only disliked papers"""
    feedback = load_feedback()
    feedback["disliked"] = []
    save_feedback(feedback)
    return RedirectResponse(url="/", status_code=303)

@app.post("/card/visible")
async def log_card_visible(card_number: str = Form(...), paper_id: str = Form(...)):
    """Log when a card becomes visible on screen"""
    print(f"👁️  Card #{card_number} is now visible (Paper ID: {paper_id})")
    return {"status": "success"}

@app.get("/proxy")
async def proxy_url(url: str):
    """Proxy external URLs to bypass X-Frame-Options"""
    try:
        # Check if it's a bioRxiv URL - they block proxying with 403
        if 'biorxiv.org' in url:
            # Return a message with a direct link
            content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        text-align: center;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 500px;
                    }}
                    h1 {{
                        font-size: 32px;
                        margin-bottom: 20px;
                    }}
                    p {{
                        font-size: 16px;
                        line-height: 1.6;
                        margin-bottom: 30px;
                        opacity: 0.9;
                    }}
                    a {{
                        display: inline-block;
                        background: white;
                        color: #667eea;
                        padding: 12px 30px;
                        border-radius: 25px;
                        text-decoration: none;
                        font-weight: 600;
                        transition: transform 0.2s;
                    }}
                    a:hover {{
                        transform: scale(1.05);
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>bioRxiv Paper</h1>
                    <p>bioRxiv doesn't allow embedding. Click the button below to open the paper in a new tab.</p>
                    <a href="{url}" target="_blank" rel="noopener noreferrer">Open Paper in New Tab</a>
                </div>
            </body>
            </html>
            """
            return HTMLResponse(content=content)
        
        # Fetch the URL for other sites (like Semantic Scholar)
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        if response.status_code == 403:
            # Site is blocking us, show a message
            content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        height: 100vh;
                        margin: 0;
                        background: #15202b;
                        color: white;
                        text-align: center;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 500px;
                    }}
                    h1 {{
                        font-size: 28px;
                        margin-bottom: 20px;
                        color: #ef4444;
                    }}
                    p {{
                        font-size: 16px;
                        line-height: 1.6;
                        margin-bottom: 30px;
                        opacity: 0.8;
                    }}
                    a {{
                        display: inline-block;
                        background: #1da1f2;
                        color: white;
                        padding: 12px 30px;
                        border-radius: 25px;
                        text-decoration: none;
                        font-weight: 600;
                        transition: transform 0.2s;
                    }}
                    a:hover {{
                        transform: scale(1.05);
                        background: #1a8cd8;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Access Blocked</h1>
                    <p>This site doesn't allow embedding. Click below to open the paper in a new tab.</p>
                    <a href="{url}" target="_blank" rel="noopener noreferrer">Open in New Tab</a>
                </div>
            </body>
            </html>
            """
            return HTMLResponse(content=content, status_code=200)
        
        # Accept any 2xx status code as success
        if response.status_code < 200 or response.status_code >= 300:
            return HTMLResponse(content=f"<h1>Error loading page</h1><p>Status code: {response.status_code}</p>", status_code=200)
        
        # Get the content
        content = response.text
        
        # Inject base tag to fix relative URLs
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Add base tag after <head>
        if '<head>' in content:
            content = content.replace('<head>', f'<head><base href="{base_url}/">')
        
        # Always return status 200 for the proxy response
        return HTMLResponse(content=content, status_code=200)
    
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error loading page</h1><p>{str(e)}</p>", status_code=200)
