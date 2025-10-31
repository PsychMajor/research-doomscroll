# Research Doomscroll - Complete Refactor Summary

## What Was Done

All bioRxiv and Semantic Scholar search functionality has been completely removed from the application. The app has been stripped down to its core infrastructure, ready for new paper sources to be integrated.

## Files Changed

### 1. `app.py` (Main Application)
- **Before**: 1,821 lines with extensive paper fetching logic
- **After**: 250 lines (86% reduction)
- **Removed**:
  - All Semantic Scholar API calls
  - All bioRxiv API calls
  - NLTK text processing
  - Paper caching system (PAPER_CACHE, DEEP_SEARCH_DATES)
  - ~1,700 lines of paper-specific code
  - Deep search functionality
  - Paper summarization
  - Interest-based filtering

### 2. `requirements.txt` (Dependencies)
- **Removed**:
  - `requests` (only used for paper APIs)
  - `aiohttp` (only used for paper APIs)
  - `sumy` (text summarization)
  - `numpy` (used by sumy)
- **Kept**:
  - `fastapi` - Web framework
  - `uvicorn` - ASGI server
  - `jinja2` - Templating
  - `python-multipart` - Form handling
  - `asyncpg` - PostgreSQL driver
  - `authlib` - OAuth
  - `httpx` - OAuth HTTP client
  - `itsdangerous` - Session security
  - `python-dotenv` - Environment variables

### 3. `templates/index.html`
- Replaced paper search interface with status page
- Shows what's still working vs. what was removed
- Clean, informative design

### 4. `templates/likes.html`
- Simplified to placeholder page
- Shows count of liked papers still in database
- Explains paper fetching will return once re-implemented

## Backups Created

All original files have been backed up:
- `app_backup_with_papers.py` - Original 1,821 line application
- `templates/index_backup.html` - Original search interface
- `templates/likes_backup.html` - Original likes page

## What's Still Working ✅

1. **Authentication System**
   - Google OAuth login/logout
   - Session management
   - User profile storage

2. **Database Infrastructure**
   - PostgreSQL with in-memory fallback
   - User management
   - Profile storage (topics, authors)
   - Feedback system (likes, dislikes)

3. **API Routes**
   - `/` - Home page
   - `/likes` - Likes page
   - `/login` - OAuth initiation
   - `/logout` - Session termination
   - `/auth/callback` - OAuth callback
   - `/profile/save` - Save user profile
   - `/profile/clear` - Clear profile
   - `/paper/like` - Like a paper
   - `/paper/unlike` - Unlike a paper
   - `/paper/dislike` - Dislike a paper
   - `/paper/undislike` - Remove dislike
   - `/feedback/clear` - Clear all feedback
   - `/card/visible` - Analytics logging
   - `/card/second-to-last` - Analytics logging

4. **Core Infrastructure**
   - FastAPI application
   - Static file serving
   - Jinja2 templates
   - Async/await support

## What Was Removed 🗑️

1. **Paper Search Functionality**
   - Semantic Scholar API integration
   - bioRxiv API integration
   - Paper fetching functions
   - Search result processing

2. **Text Processing**
   - NLTK integration
   - Abstract summarization
   - Keyword extraction
   - Interest matching algorithms

3. **Caching System**
   - In-memory paper cache
   - Deep search date tracking
   - Cache invalidation logic

4. **Search Features**
   - Topic-based search
   - Author-based search
   - Deep search functionality
   - Paper deduplication
   - Result ranking

## Next Steps

The application is now ready for new paper sources to be integrated. The infrastructure supports:

1. **Adding New Paper Sources**
   - API integration functions can be added to `app.py`
   - Use existing profile system (topics, authors)
   - Leverage existing feedback system (likes, dislikes)

2. **Recommended Approach**
   ```python
   # Example structure for new paper source
   async def fetch_papers_from_new_source(topics, authors):
       # Fetch papers from new API
       # Return standardized paper format:
       # {
       #     'id': str,
       #     'title': str,
       #     'authors': list,
       #     'abstract': str,
       #     'url': str,
       #     'date': str
       # }
       pass
   ```

3. **Update Home Route**
   - Modify `/` route in `app.py` to call new fetch function
   - Pass papers to template
   - Update `templates/index.html` to display paper cards

4. **Database Schema**
   - Current schema supports generic paper storage
   - Feedback table works with any paper ID
   - Profile system is source-agnostic

## Testing the App

To verify the infrastructure is working:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app:app --reload

# Visit http://localhost:8000
# You should see the status page with authentication working
```

## Environment Variables Needed

The app still requires these environment variables in `.env`:
```
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
SECRET_KEY=your_secret_key
DATABASE_URL=your_postgres_url (optional)
```

## Git Status

The changes have **not** been committed yet. You can:

1. **Review changes**: `git diff`
2. **Commit changes**: 
   ```bash
   git add .
   git commit -m "Remove bioRxiv and Semantic Scholar functionality"
   git push
   ```
3. **Revert if needed**: Backup files are available

## Summary

- **Reduced**: 1,821 → 250 lines in app.py (86% smaller)
- **Removed**: All paper search functionality
- **Preserved**: Authentication, database, routing, feedback
- **Backed up**: All original files saved
- **Ready**: Clean slate for new paper sources

The application is now a minimal, well-organized foundation ready for your new paper source integrations.
