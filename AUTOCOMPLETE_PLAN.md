# Google-like Autocomplete Feature Plan

## Overview
Implement a Google-like autocomplete feature that provides real-time search suggestions as users type in the search bar, using the OpenAlex API to suggest papers, authors, journals, and topics.

## Architecture

### Backend Components

#### 1. OpenAlex Autocomplete Service (`backend/services/openalex_autocomplete.py`)
- **Purpose**: Query OpenAlex API for autocomplete suggestions
- **Endpoints to query**:
  - `/works` - for paper suggestions (by title/keywords)
  - `/authors` - for author name suggestions
  - `/sources` - for journal/venue suggestions
  - `/concepts` - for topic/keyword suggestions
- **Method**: `get_autocomplete_suggestions(query: str, types: List[str] = None) -> List[Dict]`
  - Query multiple OpenAlex endpoints in parallel
  - Combine and deduplicate results
  - Return structured suggestions with type labels

#### 2. Autocomplete API Endpoint (`backend/routers/autocomplete.py`)
- **Endpoint**: `GET /api/autocomplete?q={query}&limit={limit}`
- **Parameters**:
  - `q`: Search query string (required)
  - `limit`: Maximum number of suggestions (default: 5-10)
  - `types`: Comma-separated types to search (optional: "works,authors,sources,concepts")
- **Response**: 
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
      },
      {
        "text": "Nature",
        "type": "journal",
        "count": 85000
      }
    ]
  }
  ```

#### 3. Caching Strategy
- Use in-memory cache (Redis or simple dict) for common queries
- Cache duration: 5-10 minutes
- Cache key: query string (normalized)

### Frontend Components

#### 1. Autocomplete Hook (`frontend/src/hooks/useAutocomplete.ts`)
- **Purpose**: Manage autocomplete state and API calls
- **Features**:
  - Debounce API calls (300-500ms delay)
  - Cancel in-flight requests when query changes
  - Cache results in React Query
  - Handle loading and error states

#### 2. AutocompleteDropdown Component (`frontend/src/components/Search/AutocompleteDropdown.tsx`)
- **Purpose**: Display autocomplete suggestions in a dropdown
- **Features**:
  - Positioned below search input
  - Keyboard navigation (arrow keys, Enter, Escape)
  - Mouse hover highlighting
  - Type icons/badges for different suggestion types
  - Max height with scrolling

#### 3. AutocompleteDropdown Styles (`frontend/src/components/Search/AutocompleteDropdown.css`)
- Google-like dropdown styling
- Dark green accents for active/selected items
- Smooth animations
- Responsive design

#### 4. Integration with Feed.tsx
- Add autocomplete state management
- Integrate dropdown component
- Handle suggestion selection
- Update search input when suggestion is selected

## Implementation Steps

### Phase 1: Backend Setup
1. Create `backend/services/openalex_autocomplete.py`
   - Implement parallel queries to multiple OpenAlex endpoints
   - Aggregate and rank suggestions
   - Add caching layer

2. Create `backend/routers/autocomplete.py`
   - Implement `/api/autocomplete` endpoint
   - Add request validation
   - Add error handling

3. Register autocomplete router in `backend/main.py`

### Phase 2: Frontend Setup
1. Create `frontend/src/api/autocomplete.ts`
   - Implement `getAutocomplete(query: string, limit?: number)` function

2. Create `frontend/src/hooks/useAutocomplete.ts`
   - Implement debounced autocomplete hook
   - Integrate with React Query

3. Create `frontend/src/components/Search/AutocompleteDropdown.tsx`
   - Build dropdown component
   - Add keyboard navigation
   - Add mouse interactions

4. Create `frontend/src/components/Search/AutocompleteDropdown.css`
   - Style dropdown to match Google's aesthetic
   - Add animations and transitions

### Phase 3: Integration
1. Update `frontend/src/pages/Feed.tsx`
   - Add autocomplete state
   - Integrate dropdown component
   - Handle suggestion selection
   - Handle keyboard navigation

2. Update `frontend/src/pages/Feed.css`
   - Ensure dropdown positioning works correctly
   - Add z-index for dropdown overlay

### Phase 4: Polish
1. Add loading indicators
2. Add empty state messaging
3. Optimize performance (debouncing, caching)
4. Add analytics/telemetry if needed

## Technical Details

### OpenAlex API Endpoints

1. **Works Autocomplete**:
   ```
   GET https://api.openalex.org/works?search={query}&per_page=5&select=id,title
   ```

2. **Authors Autocomplete**:
   ```
   GET https://api.openalex.org/authors?search={query}&per_page=5&select=id,display_name
   ```

3. **Sources Autocomplete**:
   ```
   GET https://api.openalex.org/sources?search={query}&per_page=5&select=id,display_name
   ```

4. **Concepts Autocomplete** (for topics):
   ```
   GET https://api.openalex.org/concepts?search={query}&per_page=5&select=id,display_name
   ```

### Debouncing Strategy
- **Initial delay**: 300ms after user stops typing
- **Minimum query length**: 2 characters before triggering autocomplete
- **Maximum requests**: Cancel previous requests when new one is made

### Caching Strategy
- **Frontend**: React Query cache (5 minutes stale time)
- **Backend**: In-memory cache with 10-minute TTL
- **Cache key**: Normalized query string (lowercase, trimmed)

### Suggestion Ranking
1. Exact matches first
2. Starts-with matches second
3. Contains matches third
4. Rank by relevance score or count if available

## UI/UX Design

### Dropdown Appearance
- Positioned directly below search input
- Same width as search input
- Maximum 5-7 suggestions visible
- Scrollable if more suggestions
- Google-like styling:
  - Subtle shadow
  - Light background
  - Hover highlighting
  - Selected item highlighting

### Suggestion Format
- **Topics**: "🔬 [Topic name]" or "[Topic name] (topic)"
- **Authors**: "👤 [Author name]" or "[Author name] (author)"
- **Journals**: "📄 [Journal name]" or "[Journal name] (journal)"
- **Papers**: "📄 [Paper title]" or "[Paper title] (paper)"

### Keyboard Navigation
- **Arrow Down**: Select next suggestion
- **Arrow Up**: Select previous suggestion
- **Enter**: Select highlighted suggestion
- **Escape**: Close dropdown
- **Tab**: Select highlighted suggestion and move focus

## Performance Considerations

1. **Debouncing**: Prevent excessive API calls
2. **Request Cancellation**: Cancel in-flight requests on new input
3. **Caching**: Cache results on both frontend and backend
4. **Parallel Requests**: Query multiple endpoints simultaneously
5. **Limit Results**: Only fetch top 5-10 suggestions per endpoint

## Error Handling

1. **Network Errors**: Show friendly error message, allow retry
2. **Empty Results**: Show "No suggestions found" message
3. **Rate Limiting**: Handle 429 errors gracefully
4. **Timeout**: Handle slow responses with loading states

## Testing Strategy

1. **Unit Tests**: Test autocomplete service logic
2. **Integration Tests**: Test API endpoint
3. **Component Tests**: Test dropdown component interactions
4. **E2E Tests**: Test full autocomplete flow

## Future Enhancements

1. Recent searches history
2. Popular searches suggestions
3. Personalization based on user history
4. Multi-language support
5. Voice search integration

