# Research Doomscroll - Next Steps Analysis

## Current State Overview

### ✅ What's Working

1. **Backend Architecture**
   - Modular FastAPI structure with routers (papers, profile, feedback, folders, auth, analytics)
   - OpenAlex API integration for paper fetching
   - Database service with PostgreSQL + in-memory fallback
   - Google OAuth authentication
   - Paper search with pagination
   - Paper caching in database
   - User feedback system (likes/dislikes)
   - Folder management system

2. **Frontend Architecture**
   - React + TypeScript with React Router
   - React Query for data fetching and caching
   - API client with axios and interceptors
   - Custom hooks (usePapers, useFeedback, useFolders, useAuth, useProfile)
   - Component structure (PaperCard, FolderCard, etc.)
   - Feed page with infinite scroll
   - Basic UI components (LoadingSpinner, ErrorMessage)

3. **Key Features Implemented**
   - Paper search by topics/authors
   - Infinite scroll pagination
   - Like/dislike papers
   - Create/manage folders
   - User authentication
   - Profile management (topics, authors)

---

## 🚧 Missing/Incomplete Features

### 1. **Recommendations Endpoint** (High Priority)
**Status**: Frontend calls it, backend missing

**Location**: 
- Frontend: `frontend/src/api/papers.ts` line 52-68
- Frontend: `frontend/src/hooks/usePapers.ts` line 39-45
- Backend: Missing in `backend/routers/papers.py`

**What's Needed**:
```python
@router.get("/recommendations", response_model=List[Paper])
async def get_recommendations(
    limit: int = Query(20, ge=1, le=100),
    user_id: int = Depends(require_user_id),
    db: DatabaseService = Depends(get_db_service),
    openalex: OpenAlexService = Depends(get_openalex_service)
):
    """
    Get personalized paper recommendations based on:
    - User's liked papers
    - User's profile topics/authors
    - Similar papers to liked ones
    """
```

**Implementation Strategy**:
- Load user's profile (topics, authors)
- Load user's liked papers
- Use OpenAlex to fetch papers based on profile
- Optionally: Use OpenAlex "related works" API for similar papers
- Return combined results

---

### 2. **Similar Papers Endpoint** (High Priority)
**Status**: Frontend calls it, backend missing

**Location**:
- Frontend: `frontend/src/api/papers.ts` line 71-88
- Frontend: `frontend/src/hooks/usePapers.ts` line 48-54
- Backend: Missing in `backend/routers/papers.py`

**What's Needed**:
```python
@router.get("/{paper_id}/similar", response_model=List[Paper])
async def get_similar_papers(
    paper_id: str,
    limit: int = Query(10, ge=1, le=50),
    openalex: OpenAlexService = Depends(get_openalex_service),
    db: DatabaseService = Depends(get_db_service)
):
    """
    Get papers similar to the given paper.
    Uses OpenAlex related works or citation network.
    """
```

**Implementation Strategy**:
- Fetch paper from OpenAlex (includes related works)
- Use OpenAlex API's related works endpoint
- Or use citation network (papers that cite/are cited by this paper)
- Cache results in database

---

### 3. **Likes Page Implementation** (High Priority)
**Status**: Currently just shows loading spinner

**Location**: `frontend/src/pages/Likes.tsx`

**What's Needed**:
- Fetch user's liked papers from feedback API
- Fetch full paper data for liked paper IDs
- Display papers in a grid/list similar to Feed page
- Allow unlike functionality
- Show empty state when no likes

**Implementation Steps**:
1. Use `useFeedback` hook to get liked paper IDs
2. Use `usePapers` hook or create bulk fetch for paper details
3. Display papers using `PaperCard` component
4. Add unlike button/functionality

---

### 4. **Profile-Based Feed Auto-Load** (Medium Priority)
**Status**: Feed requires manual search, doesn't auto-load from profile

**Location**: `frontend/src/pages/Feed.tsx`

**What's Needed**:
- On page load, check if user has saved profile
- If profile exists, automatically trigger search with profile topics/authors
- Show "Loading your personalized feed..." message
- Allow user to override with manual search

**Implementation Steps**:
1. Use `useProfile` hook to load user profile
2. Use `useEffect` to auto-trigger search when profile loads
3. Update UI to show profile-based search vs manual search

---

### 5. **OpenAlex Related Works Integration** (Medium Priority)
**Status**: OpenAlex service doesn't fetch related works

**Location**: `backend/services/openalex_service.py`

**What's Needed**:
- Add method to fetch related works for a paper
- OpenAlex API provides `related_works` in work objects
- Can also use `/works/{id}/related_works` endpoint

**Implementation**:
```python
async def fetch_related_works(self, paper_id: str, limit: int = 10) -> List[Paper]:
    """Fetch related works for a paper"""
    # Use OpenAlex related works endpoint or related_works field
```

---

### 6. **Error Handling Improvements** (Medium Priority)
**Status**: Basic error handling exists, but could be improved

**Areas to Improve**:
- Better error messages for API failures
- Retry logic for transient failures
- User-friendly error messages in UI
- Handle rate limiting from OpenAlex
- Handle network timeouts gracefully

---

### 7. **CORS/Proxy Configuration** (Low Priority)
**Status**: May need configuration for development

**What to Check**:
- Vite proxy configuration in `vite.config.ts`
- CORS settings in FastAPI if serving from different origins
- Session cookie handling across origins

---

### 8. **Paper Detail View** (Low Priority)
**Status**: No dedicated page for viewing a single paper

**What's Needed**:
- Route: `/papers/:paperId`
- Show full paper details
- Show similar papers
- Show related papers
- Allow like/dislike
- Allow adding to folders

---

### 9. **Search History/Saved Searches** (Low Priority)
**Status**: Not implemented

**What's Needed**:
- Save recent searches
- Allow quick re-search of saved queries
- Store in user profile or separate table

---

### 10. **API Endpoint Mismatches** (High Priority - Bug Fix)
**Status**: Frontend calling wrong endpoints

**Issues Found**:
- `frontend/src/api/profile.ts` calls `/profile` but backend is at `/api/profile`
- `frontend/src/api/profile.ts` calls `/profile/interests` and `/profile/liked-papers` which don't exist
- Backend profile router only has: `GET /api/profile`, `PUT /api/profile`, `DELETE /api/profile`

**What's Needed**:
- Fix frontend API calls to match backend routes
- Or add missing backend endpoints
- Profile API should use `/api/profile` prefix

### 11. **Analytics Integration** (Low Priority)
**Status**: Analytics router exists but may need frontend integration

**Location**: `backend/routers/analytics.py`

**What to Check**:
- Are analytics events being sent from frontend?
- What analytics are being tracked?
- Do we need to add more tracking?

---

## 🎯 Recommended Implementation Order

### Phase 1: Critical Fixes & Core Features (Week 1)
1. ✅ **Fix API Endpoint Mismatches** - Profile API routes (URGENT)
2. ✅ **Similar Papers Endpoint** - Enables paper discovery
3. ✅ **Recommendations Endpoint** - Personalized feed
4. ✅ **Likes Page Implementation** - View saved papers

### Phase 2: UX Improvements (Week 2)
5. ✅ **Profile-Based Auto-Load** - Better onboarding
6. ✅ **OpenAlex Related Works** - Better recommendations
7. ✅ **Error Handling** - Better user experience

### Phase 3: Polish & Features (Week 3+)
8. ✅ **Paper Detail View** - Deep dive into papers
9. ✅ **Search History** - Convenience feature
10. ✅ **Analytics Integration** - Usage insights

---

## 🔍 Technical Debt & Improvements

### Code Quality
- [ ] Add comprehensive error logging
- [ ] Add unit tests for services
- [ ] Add integration tests for API endpoints
- [ ] Add TypeScript strict mode checks
- [ ] Add ESLint/Prettier configuration

### Performance
- [ ] Implement request caching for OpenAlex API
- [ ] Add database query optimization
- [ ] Implement pagination for folders
- [ ] Add lazy loading for images

### Security
- [ ] Review authentication flow
- [ ] Add rate limiting
- [ ] Validate all user inputs
- [ ] Sanitize user-generated content

### Documentation
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Frontend component documentation
- [ ] Setup/deployment guide
- [ ] Architecture decision records

---

## 📝 Quick Wins

These can be implemented quickly for immediate value:

1. **Likes Page** - ~2 hours
   - Use existing hooks and components
   - Just needs to fetch and display

2. **Similar Papers Endpoint** - ~3 hours
   - OpenAlex API already provides related works
   - Just need to expose it

3. **Profile Auto-Load** - ~2 hours
   - Use existing profile hook
   - Auto-trigger search on load

---

## 🚀 Getting Started

To start implementing, I recommend:

1. **Start with Similar Papers Endpoint** - It's straightforward and provides immediate value
2. **Then implement Likes Page** - Uses existing infrastructure
3. **Then Recommendations** - More complex but high value

Would you like me to start implementing any of these features?

