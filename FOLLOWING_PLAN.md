# Following Feature Implementation Plan

## Overview
Allow users to follow authors, institutions, topics, and sources individually. Each follow is stored separately, and when displaying the feed, make separate API calls for each followed item, then merge and sort results by recency.

## Architecture

### Backend Components

#### 1. Database Schema (Firebase)
- **Collection: `follows`**
  - Document ID: `{userId}_{type}_{entityId}`
  - Fields:
    - `userId`: string
    - `type`: "author" | "institution" | "topic" | "source"
    - `entityId`: string (OpenAlex ID)
    - `entityName`: string (display name)
    - `followedAt`: timestamp
    - `openalexId`: string (for API calls)

#### 2. Follow Service (`backend/services/follow_service.py`)
- **Methods:**
  - `follow_entity(user_id, entity_type, entity_id, entity_name, openalex_id)`: Add a follow
  - `unfollow_entity(user_id, entity_type, entity_id)`: Remove a follow
  - `get_user_follows(user_id)`: Get all follows for a user
  - `get_followed_papers(user_id)`: Fetch papers from all followed entities and merge

#### 3. Follow API Router (`backend/routers/follows.py`)
- **Endpoints:**
  - `POST /api/follows` - Follow an entity
    - Body: `{ type: "author" | "institution" | "topic" | "source", entityId: string, entityName: string, openalexId: string }`
  - `DELETE /api/follows/{type}/{entityId}` - Unfollow an entity
  - `GET /api/follows` - Get all user's follows
  - `GET /api/follows/papers` - Get merged papers from all follows (sorted by recency)

#### 4. Entity Search Service (`backend/services/entity_search_service.py`)
- **Methods:**
  - `search_authors(query, limit)`: Search OpenAlex authors
  - `search_institutions(query, limit)`: Search OpenAlex institutions
  - `search_topics(query, limit)`: Search OpenAlex concepts
  - `search_sources(query, limit)`: Search OpenAlex sources

#### 5. Entity Search API Router (`backend/routers/entity_search.py`)
- **Endpoints:**
  - `GET /api/entity-search/authors?q={query}&limit={limit}`
  - `GET /api/entity-search/institutions?q={query}&limit={limit}`
  - `GET /api/entity-search/topics?q={query}&limit={limit}`
  - `GET /api/entity-search/sources?q={query}&limit={limit}`

### Frontend Components

#### 1. Entity Search Hook (`frontend/src/hooks/useEntitySearch.ts`)
- Search for authors, institutions, topics, sources
- Debounced API calls
- React Query integration

#### 2. Follow Hook (`frontend/src/hooks/useFollows.ts`)
- `useFollows()`: Get all user's follows
- `useFollowEntity()`: Follow mutation
- `useUnfollowEntity()`: Unfollow mutation
- `useFollowedPapers()`: Get merged papers from all follows

#### 3. Entity Search Component (`frontend/src/components/Follow/EntitySearch.tsx`)
- Search input with autocomplete
- Display search results with follow buttons
- Filter by type (author, institution, topic, source)

#### 4. Followed Entities List (`frontend/src/components/Follow/FollowedEntitiesList.tsx`)
- Display all followed items grouped by type
- Unfollow buttons
- Show entity names and types

#### 5. Update Home Page (`frontend/src/pages/Home.tsx`)
- Add entity search to "Following" tab
- Display followed entities list
- Show merged feed from all follows

## Implementation Steps

### Phase 1: Backend - Entity Search
1. Create `entity_search_service.py` with OpenAlex search methods
2. Create `entity_search.py` router with search endpoints
3. Register router in `main.py`

### Phase 2: Backend - Follow Management
1. Create `follow_service.py` with Firebase operations
2. Create `follows.py` router with CRUD endpoints
3. Register router in `main.py`

### Phase 3: Backend - Followed Papers Feed
1. Implement `get_followed_papers()` in `follow_service.py`
2. Make parallel API calls to OpenAlex for each followed entity
3. Merge and sort results by publication date (most recent first)
4. Add endpoint `/api/follows/papers`

### Phase 4: Frontend - Entity Search
1. Create `useEntitySearch` hook
2. Create `EntitySearch` component
3. Add search UI to "Following" tab

### Phase 5: Frontend - Follow Management
1. Create `useFollows` hook
2. Create `FollowedEntitiesList` component
3. Add follow/unfollow functionality

### Phase 6: Frontend - Feed Integration
1. Create `useFollowedPapers` hook
2. Update "Following" tab to show merged feed
3. Add loading and error states

## Technical Details

### OpenAlex API Endpoints for Entity Search

1. **Authors**: `GET https://api.openalex.org/authors?search={query}&per_page={limit}`
2. **Institutions**: `GET https://api.openalex.org/institutions?search={query}&per_page={limit}`
3. **Topics/Concepts**: `GET https://api.openalex.org/concepts?search={query}&per_page={limit}`
4. **Sources**: `GET https://api.openalex.org/sources?search={query}&per_page={limit}`

### OpenAlex API for Papers by Entity

1. **Papers by Author**: `GET https://api.openalex.org/works?filter=authorships.author.id:{authorId}&sort=publication_date:desc`
2. **Papers by Institution**: `GET https://api.openalex.org/works?filter=authorships.institutions.id:{institutionId}&sort=publication_date:desc`
3. **Papers by Topic**: `GET https://api.openalex.org/works?filter=concepts.id:{conceptId}&sort=publication_date:desc`
4. **Papers by Source**: `GET https://api.openalex.org/works?filter=primary_location.source.id:{sourceId}&sort=publication_date:desc`

### Data Flow

1. **User searches for entity** → Entity search API → Display results
2. **User clicks "Follow"** → POST /api/follows → Store in Firebase
3. **Display Following feed** → GET /api/follows/papers → 
   - Backend fetches all follows
   - Makes parallel API calls to OpenAlex for each
   - Merges results
   - Sorts by publication_date (desc)
   - Returns combined list

### Merging Strategy

- Fetch papers from all followed entities in parallel
- Combine all results into single array
- Sort by `publication_date` descending (most recent first)
- Deduplicate by paper ID
- Limit total results (e.g., 200 most recent)

## UI/UX Design

### Entity Search Interface
- Search input with type selector (Author/Institution/Topic/Source)
- Results list showing:
  - Entity name
  - Type badge
  - "Follow" button
  - OpenAlex ID (for reference)

### Followed Entities Display
- Grouped by type (Authors, Institutions, Topics, Sources)
- Each item shows:
  - Entity name
  - Type badge
  - "Unfollow" button
- Collapsible sections per type

### Following Feed
- Same paper card format as other feeds
- Papers sorted by most recent publication date
- Infinite scroll support
- Loading states for each entity fetch

## Error Handling

1. **Entity not found**: Show friendly message
2. **Already following**: Prevent duplicate follows
3. **API rate limits**: Handle gracefully with retries
4. **Network errors**: Show retry options
5. **Empty follows**: Show helpful empty state

## Performance Considerations

1. **Parallel API calls**: Use `asyncio.gather()` for all entity fetches
2. **Caching**: Cache followed papers for 5-10 minutes
3. **Pagination**: Support pagination for large follow lists
4. **Debouncing**: Debounce entity search queries
5. **Optimistic updates**: Update UI immediately on follow/unfollow

## Future Enhancements

1. Follow notifications for new papers
2. Follow suggestions based on user interests
3. Bulk follow/unfollow operations
4. Follow statistics (number of papers, last update, etc.)
5. Export followed entities list

