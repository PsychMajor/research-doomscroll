from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv
import os
import json
import requests
import asyncio
from datetime import datetime
import database

# Sumy imports for text summarization
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Add session middleware for OAuth
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production-use-python-secrets")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Configure OAuth
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@app.on_event("startup")
async def startup_event():
    """Initialize database connection pool on startup"""
    await database.init_db()
    print("✅ Database initialized")
    
    # Download required NLTK data
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)
        print("✅ NLTK data loaded")
    except Exception as e:
        print(f"⚠️  NLTK data download warning: {e}")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# ============================================================================
# TEXT SUMMARIZATION
# ============================================================================

def format_scientific_text(text):
    """
    Convert scientific notation to HTML with proper subscripts and superscripts
    
    Examples:
        β2 -> β<sub>2</sub>
        10^6 -> 10<sup>6</sup>
        CO2 -> CO<sub>2</sub>
    """
    import re
    
    if not text:
        return text
    
    # Convert subscripts (e.g., β2, H2O, CO2)
    # Pattern: letter followed by digit(s)
    text = re.sub(r'([A-Za-zα-ωΑ-Ω])(\d+)', r'\1<sub>\2</sub>', text)
    
    # Convert superscripts (e.g., 10^6, x^2)
    # Pattern: ^digit or ^{digits}
    text = re.sub(r'\^(\d+)', r'<sup>\1</sup>', text)
    text = re.sub(r'\^\{([^}]+)\}', r'<sup>\1</sup>', text)
    
    return text

def summarize_text(text, sentences_count=2):
    """
    Summarize text using LSA (Latent Semantic Analysis) algorithm
    
    Args:
        text: The text to summarize
        sentences_count: Number of sentences in the summary
    
    Returns:
        Summarized text string
    """
    if not text or len(text.strip()) < 50:
        return None
    
    try:
        # Parse the text
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        
        # Create LSA summarizer
        summarizer = LsaSummarizer()
        
        # Generate summary
        summary_sentences = summarizer(parser.document, sentences_count=sentences_count)
        
        # Join sentences into a single string
        summary = " ".join([str(sentence) for sentence in summary_sentences])
        
        return summary if summary else None
        
    except Exception as e:
        print(f"⚠️  Summarization error: {e}")
        # Fallback to first N characters
        if len(text) > 200:
            return text[:200].rsplit(" ", 1)[0] + "..."
        return None

# ============================================================================
# OPENALEX API CONFIGURATION
# ============================================================================

# OpenAlex Polite Pool - add your email to get faster API access
OPENALEX_EMAIL = os.environ.get("OPENALEX_EMAIL", "your-email@example.com")
OPENALEX_API_URL = "https://api.openalex.org/works"
OPENALEX_AUTHORS_URL = "https://api.openalex.org/authors"

# Helper function to get author IDs from names
def get_author_ids(author_names):
    """
    Query OpenAlex authors endpoint to get author IDs from names
    
    Args:
        author_names: List of author names to search for
    
    Returns:
        List of OpenAlex author IDs
    """
    author_ids = []
    
    for name in author_names:
        try:
            params = {
                "mailto": OPENALEX_EMAIL,
                "search": name,
                "per_page": 1  # Just get the top match
            }
            
            response = requests.get(OPENALEX_AUTHORS_URL, params=params, timeout=10)
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

# Helper function to fetch from OpenAlex
def fetch_openalex_papers(topics=None, authors=None, per_page=25, page=1, sort_by="relevance"):
    """
    Fetch papers from OpenAlex API using the polite pool
    
    Args:
        topics: List of topic keywords
        authors: List of author names
        per_page: Number of results per page (max 200)
        page: Page number
        sort_by: Sort order - "relevance" (citations) or "recency" (newest first)
    
    Returns:
        List of standardized paper dictionaries
    """
    
    # Determine sort parameter
    if sort_by == "recency":
        sort_param = "publication_date:desc"
    else:  # default to relevance (citations)
        sort_param = "cited_by_count:desc"
    
    # Build request parameters
    params = {
        "mailto": OPENALEX_EMAIL,  # Polite pool access
        "per_page": per_page,
        "page": page,
        "sort": sort_param,
        "select": "id,title,abstract_inverted_index,primary_location,doi,publication_year,cited_by_count,authorships",  # Explicitly request fields including abstract
    }
    
    # Build filters - OpenAlex requires using filter parameter (not search + filter together)
    filters = []
    
    # Get author IDs if authors are provided
    author_ids = []
    if authors:
        print(f"🔍 Looking up author IDs for: {authors}")
        author_ids = get_author_ids(authors)
        if not author_ids:
            print(f"   ⚠️ No author IDs found, will search by name instead")
    
    # Add topic search using the search parameter (works better than filter for text search)
    if topics:
        topic_query = " ".join(topics)
        params["search"] = topic_query
    
    # Add author filters using author IDs
    if author_ids:
        # Use author.id filter with the OpenAlex author IDs
        # Multiple authors use OR logic (|)
        author_filter = "|".join([f"author.id:{aid}" for aid in author_ids])
        filters.append(author_filter)
    elif authors and not author_ids:
        # Fallback: if we couldn't get IDs, add authors to search parameter
        if not topics:
            params["search"] = " ".join(authors)
        else:
            params["search"] = params["search"] + " " + " ".join(authors)
    
    # Add filters to params
    if filters:
        params["filter"] = ",".join(filters)
    
    try:
        print(f"🔍 Fetching from OpenAlex: page={page}, topics={topics}, authors={authors}, sort={sort_by}")
        print(f"   Search: {params.get('search', 'N/A')}")
        print(f"   Filter: {params.get('filter', 'N/A')}")
        response = requests.get(OPENALEX_API_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        papers = []
        
        for work in data.get("results", []):
            # Extract paper information
            paper = {
                "paperId": work.get("id", "").split("/")[-1],  # Extract ID from URL
                "title": format_scientific_text(work.get("title", "Untitled")),  # Format title with sub/superscripts
                "abstract": work.get("abstract_inverted_index"),  # OpenAlex uses inverted index
                "url": work.get("primary_location", {}).get("landing_page_url") or work.get("doi"),
                "year": work.get("publication_year"),
                "citationCount": work.get("cited_by_count", 0),
                "authors": [],
                "venue": None,
                "source": "OpenAlex",
                "tldr": None
            }
            
            # Convert inverted index to abstract text if available
            if paper["abstract"] and isinstance(paper["abstract"], dict):
                try:
                    # Reconstruct abstract from inverted index
                    # The inverted index maps words to their positions in the text
                    word_positions = []
                    for word, positions in paper["abstract"].items():
                        if positions:  # Make sure positions list is not empty
                            for pos in positions:
                                word_positions.append((pos, word))
                    
                    # Sort by position and join words
                    if word_positions:
                        word_positions.sort(key=lambda x: x[0])
                        abstract_text = " ".join([word for _, word in word_positions])
                        paper["abstract"] = format_scientific_text(abstract_text)  # Format with sub/superscripts
                    else:
                        paper["abstract"] = None
                except Exception as e:
                    print(f"⚠️  Error reconstructing abstract: {e}")
                    paper["abstract"] = None
            else:
                paper["abstract"] = None
            
            # Extract authors
            for authorship in work.get("authorships", [])[:10]:  # Limit to first 10 authors
                author_info = authorship.get("author", {})
                if author_info.get("display_name"):
                    paper["authors"].append({
                        "name": author_info.get("display_name")
                    })
            
            # Extract venue/journal
            primary_location = work.get("primary_location", {})
            if primary_location:
                source = primary_location.get("source", {})
                if source:
                    paper["venue"] = source.get("display_name")
            
            # Generate TL;DR using text summarization
            if paper["abstract"]:
                paper["tldr"] = summarize_text(paper["abstract"], sentences_count=2)
            
            papers.append(paper)
        
        print(f"✅ Fetched {len(papers)} papers from OpenAlex")
        return papers
        
    except requests.exceptions.RequestException as e:
        print(f"❌ OpenAlex API error: {e}")
        return []
    except Exception as e:
        print(f"❌ Error processing OpenAlex data: {e}")
        return []


async def fetch_paper_by_openalex_id(openalex_id: str):
    """
    Fetch a single paper from OpenAlex by its ID
    
    Args:
        openalex_id: OpenAlex paper ID (e.g., "W2104477830" or "https://openalex.org/W2104477830")
    
    Returns:
        Paper dict or None if not found
    """
    try:
        # Clean the ID - extract just the W... part if it's a URL
        if openalex_id.startswith('http'):
            openalex_id = openalex_id.split('/')[-1]
        
        # Ensure it starts with W
        if not openalex_id.startswith('W'):
            openalex_id = f"W{openalex_id}"
        
        url = f"https://api.openalex.org/works/{openalex_id}"
        
        params = {}
        if OPENALEX_EMAIL:
            params['mailto'] = OPENALEX_EMAIL
        
        print(f"🔍 Fetching paper from OpenAlex: {openalex_id}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        work = response.json()
        
        # Extract abstract from inverted index
        abstract_text = ""
        if work.get("abstract_inverted_index"):
            inverted = work["abstract_inverted_index"]
            words = [""] * (max(max(positions) for positions in inverted.values()) + 1)
            for word, positions in inverted.items():
                for pos in positions:
                    words[pos] = word
            abstract_text = " ".join(words)
        
        # Format authors
        authors = []
        if work.get("authorships"):
            for authorship in work["authorships"][:10]:  # Limit to 10 authors
                author_data = authorship.get("author", {})
                authors.append({
                    "name": author_data.get("display_name", "Unknown Author")
                })
        
        # Generate TL;DR from abstract
        tldr = summarize_text(abstract_text, sentences_count=2) if abstract_text else None
        
        # Format the paper
        paper = {
            "paperId": openalex_id,
            "title": format_scientific_text(work.get("title", "Untitled")),
            "authors": authors,
            "abstract": format_scientific_text(abstract_text) if abstract_text else "",
            "year": work.get("publication_year"),
            "venue": work.get("primary_location", {}).get("source", {}).get("display_name", ""),
            "citationCount": work.get("cited_by_count", 0),
            "url": work.get("primary_location", {}).get("landing_page_url") or work.get("doi", ""),
            "source": "OpenAlex",
            "tldr": tldr
        }
        
        print(f"✅ Fetched paper: {paper['title'][:50]}...")
        return paper
        
    except requests.exceptions.RequestException as e:
        print(f"❌ OpenAlex API error fetching paper {openalex_id}: {e}")
        return None
    except Exception as e:
        print(f"❌ Error processing OpenAlex paper {openalex_id}: {e}")
        return None


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

def get_current_user(request: Request):
    """Get current user from session, return anonymous user if not logged in"""
    user = request.session.get('user')
    if user:
        return user
    # Return anonymous user
    return {
        'id': 'anonymous',
        'email': 'anonymous@example.com',
        'name': 'Anonymous User',
        'picture': ''
    }

@app.get("/login")
async def login(request: Request):
    """Initiate Google OAuth login"""
    redirect_uri = request.url_for('auth_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/callback")
async def auth_callback(request: Request):
    """Handle OAuth callback"""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if user_info:
            # Store user in session
            request.session['user'] = {
                'id': user_info['sub'],
                'email': user_info['email'],
                'name': user_info.get('name', ''),
                'picture': user_info.get('picture', '')
            }
            
            # Create or update user in database
            await database.create_or_update_user(
                user_id=user_info['sub'],
                email=user_info['email'],
                name=user_info.get('name', ''),
                picture=user_info.get('picture', '')
            )
    except Exception as e:
        print(f"OAuth error: {e}")
    
    return RedirectResponse(url='/')

@app.get("/logout")
async def logout(request: Request):
    """Logout user"""
    request.session.pop('user', None)
    return RedirectResponse(url='/')

# ============================================================================
# MAIN ROUTES
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, topics: str = "", authors: str = "", sort_by: str = "relevance"):
    """Main homepage"""
    user = get_current_user(request)
    user_id = user['id']
    
    # Load user's profile and feedback
    profile = await database.load_profile(user_id=user_id)
    feedback = await database.load_feedback(user_id=user_id)
    
    # Parse topics and authors from query params or use profile
    topics_list = [t.strip() for t in topics.split(',') if t.strip()] if topics else profile.get("topics", [])
    authors_list = [a.strip() for a in authors.split(',') if a.strip()] if authors else profile.get("authors", [])
    
    # Fetch papers from OpenAlex if we have topics or authors
    papers = []
    if topics_list or authors_list:
        papers = fetch_openalex_papers(topics=topics_list, authors=authors_list, per_page=25, sort_by=sort_by)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user,
        "papers": papers,
        "show_form": True,
        "topics": ", ".join(topics_list),
        "authors": ", ".join(authors_list),
        "sort_by": sort_by,
        "profile": profile,
        "feedback": feedback
    })

@app.get("/likes", response_class=HTMLResponse)
async def get_likes(request: Request):
    """Display all liked papers"""
    user = get_current_user(request)
    user_id = user['id']
    
    # Load user's feedback
    feedback = await database.load_feedback(user_id=user_id)
    profile = await database.load_profile(user_id=user_id)
    
    # Fetch actual paper details from database
    liked_paper_ids = feedback.get('liked', [])
    papers = []
    
    if liked_paper_ids:
        # First, try to get papers from database
        papers = await database.get_papers_by_ids(liked_paper_ids)
        papers_dict = {p['paperId']: p for p in papers}
        
        # For any missing papers, fetch from OpenAlex
        missing_ids = [pid for pid in liked_paper_ids if pid not in papers_dict]
        
        if missing_ids:
            print(f"📥 Fetching {len(missing_ids)} missing papers from OpenAlex...")
            for paper_id in missing_ids:
                paper = await fetch_paper_by_openalex_id(paper_id)
                if paper:
                    # Save to database for future use
                    await database.save_paper(paper)
                    papers.append(paper)
                    print(f"   ✅ Fetched and saved: {paper['title'][:50]}...")
        
        # Sort papers by the order in liked_paper_ids (most recent first)
        papers_dict = {p['paperId']: p for p in papers}
        papers = [papers_dict[pid] for pid in liked_paper_ids if pid in papers_dict]
    
    return templates.TemplateResponse("likes.html", {
        "request": request,
        "user": user,
        "papers": papers,
        "liked_paper_ids": liked_paper_ids,
        "feedback": feedback,
        "profile": profile,
        "show_form": False
    })

# ============================================================================
# PROFILE ROUTES
# ============================================================================

@app.post("/profile/save")
async def save_profile_endpoint(request: Request, topics: str = Form(""), authors: str = Form(""), sort_by: str = Form("relevance")):
    """Save user profile"""
    user = get_current_user(request)
    user_id = user['id']
    
    topics_list = [t.strip() for t in topics.split(',') if t.strip()]
    authors_list = [a.strip() for a in authors.split(',') if a.strip()]
    
    await database.save_profile(topics_list, authors_list, user_id=user_id)
    
    # Redirect to home with sort_by parameter
    if topics or authors:
        return RedirectResponse(url=f"/?topics={topics}&authors={authors}&sort_by={sort_by}", status_code=303)
    return RedirectResponse(url="/", status_code=303)

@app.get("/profile")
async def get_profile(request: Request):
    """Get current profile as JSON"""
    user = get_current_user(request)
    return await database.load_profile(user_id=user['id'])

@app.post("/profile/clear")
async def clear_profile_endpoint(request: Request):
    """Clear user profile"""
    user = get_current_user(request)
    await database.save_profile([], [], user_id=user['id'])
    return RedirectResponse(url="/", status_code=303)

# ============================================================================
# FEEDBACK ROUTES (Like/Dislike)
# ============================================================================

@app.post("/paper/like")
async def like_paper_endpoint(request: Request, paper_id: str = Form(...), paper_data: str = Form(None)):
    """Like a paper and save its metadata"""
    user = get_current_user(request)
    
    # Save paper metadata if provided
    if paper_data:
        try:
            paper_dict = json.loads(paper_data)
            await database.save_paper(paper_dict)
        except Exception as e:
            print(f"⚠️  Error parsing paper data: {e}")
    
    await database.like_paper(paper_id, user_id=user['id'])
    return {"status": "success"}

@app.post("/paper/unlike")
async def unlike_paper_endpoint(request: Request, paper_id: str = Form(...)):
    """Unlike a paper"""
    user = get_current_user(request)
    await database.unlike_paper(paper_id, user_id=user['id'])
    return {"status": "success"}

@app.post("/paper/dislike")
async def dislike_paper_endpoint(request: Request, paper_id: str = Form(...), paper_data: str = Form(None)):
    """Dislike a paper and save its metadata"""
    user = get_current_user(request)
    
    # Save paper metadata if provided
    if paper_data:
        try:
            paper_dict = json.loads(paper_data)
            await database.save_paper(paper_dict)
        except Exception as e:
            print(f"⚠️  Error parsing paper data: {e}")
    
    await database.dislike_paper(paper_id, user_id=user['id'])
    return {"status": "success"}

@app.post("/paper/undislike")
async def undislike_paper_endpoint(request: Request, paper_id: str = Form(...)):
    """Undislike a paper"""
    user = get_current_user(request)
    await database.undislike_paper(paper_id, user_id=user['id'])
    return {"status": "success"}

@app.get("/feedback")
async def get_feedback_endpoint(request: Request):
    """Get user feedback as JSON"""
    user = get_current_user(request)
    return await database.load_feedback(user_id=user['id'])

@app.post("/feedback/clear")
async def clear_all_feedback_endpoint(request: Request):
    """Clear all user feedback"""
    user = get_current_user(request)
    await database.clear_feedback(user_id=user['id'])
    return RedirectResponse(url="/", status_code=303)

@app.post("/feedback/clear/liked")
async def clear_liked_endpoint(request: Request):
    """Clear liked papers"""
    user = get_current_user(request)
    await database.clear_liked(user_id=user['id'])
    return RedirectResponse(url="/", status_code=303)

@app.post("/feedback/clear/disliked")
async def clear_disliked_endpoint(request: Request):
    """Clear disliked papers"""
    user = get_current_user(request)
    await database.clear_disliked(user_id=user['id'])
    return RedirectResponse(url="/", status_code=303)

# ============================================================================
# TRACKING ROUTES (Optional analytics)
# ============================================================================

@app.post("/card/visible")
async def log_card_visible(request: Request, card_number: int = Form(...), paper_id: str = Form(...)):
    """Log when a card becomes visible"""
    print(f"👁️  Card #{card_number} is now visible (Paper ID: {paper_id})")
    return {"status": "success"}

@app.post("/card/second-to-last")
async def log_second_to_last(request: Request, card_number: int = Form(...), paper_id: str = Form(...), total_cards: int = Form(...)):
    """Log when user views second-to-last card"""
    print(f"🔔 SECOND-TO-LAST CARD: User viewing card #{card_number} (Paper ID: {paper_id}) - {card_number} of {total_cards} cards")
    return {"status": "success"}
