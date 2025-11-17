# Twitter-like Caching System Implementation Plan

## Overview
Implement a comprehensive caching system that preserves user progress (scroll position, loaded data, form state) when navigating between pages, similar to Twitter's behavior.

## Goals
1. **Scroll Position Restoration**: Return to exact scroll position when navigating back
2. **Feed State Persistence**: Preserve loaded papers, search params, and pagination state
3. **Form State Persistence**: Keep form inputs (topics, authors, sortBy) when navigating away
4. **React Query Cache Persistence**: Persist query cache to survive page refreshes
5. **Page-specific State**: Each page maintains its own cached state independently

## Architecture

### 1. Scroll Position Manager
**Location**: `frontend/src/utils/scrollManager.ts`
- Save scroll position with a unique key per page/route
- Restore scroll position on component mount
- Use `sessionStorage` for temporary persistence (cleared on tab close)
- Handle scroll restoration after DOM is ready

### 2. Feed State Cache
**Location**: `frontend/src/hooks/useFeedCache.ts`
- Store search parameters (topics, authors, sortBy)
- Store active search state
- Store form input values
- Use `sessionStorage` for persistence
- Provide hooks to save/restore feed state

### 3. React Query Persistence
**Location**: `frontend/src/utils/queryCachePersister.ts`
- Persist React Query cache to `localStorage`
- Restore cache on app initialization
- Use `persistQueryClient` from `@tanstack/react-query-persist-client`
- Configure cache size limits and expiration

### 4. Page State Manager
**Location**: `frontend/src/hooks/usePageState.ts`
- Generic hook for managing page-specific state
- Save/restore state per route
- Handle cleanup on unmount
- Support multiple pages simultaneously

## Implementation Steps

### Phase 1: Scroll Position Management
1. Create `scrollManager.ts` utility
2. Integrate into Feed component
3. Add scroll restoration on mount
4. Test navigation between pages

### Phase 2: Feed State Persistence
1. Create `useFeedCache.ts` hook
2. Save form state (topics, authors, sortBy)
3. Save active search params
4. Restore state on component mount
5. Clear cache when new search is initiated

### Phase 3: React Query Cache Persistence
1. Install `@tanstack/react-query-persist-client`
2. Create query cache persister
3. Configure in App.tsx
4. Set cache expiration (e.g., 24 hours)
5. Test cache restoration after page refresh

### Phase 4: Page State Manager
1. Create `usePageState.ts` hook
2. Implement per-route state storage
3. Add to Feed, Likes, Folders pages
4. Test state preservation across navigation

### Phase 5: Integration & Testing
1. Integrate all components
2. Test complete user flow
3. Handle edge cases (cache size, expiration)
4. Add cleanup on logout
5. Performance optimization

## Technical Details

### Storage Strategy
- **sessionStorage**: For temporary state (scroll position, form inputs)
  - Cleared when tab closes
  - Faster access
  - Per-tab isolation
  
- **localStorage**: For React Query cache
  - Survives page refresh
  - Larger storage capacity
  - Shared across tabs

### Cache Keys
- Scroll positions: `scroll:${route}`
- Feed state: `feed:state`
- Form inputs: `feed:form:${field}`
- React Query: `REACT_QUERY_OFFLINE_CACHE`

### State Structure
```typescript
interface FeedCacheState {
  topics: string;
  authors: string;
  sortBy: 'recency' | 'relevance';
  activeSearch: SearchParams | null;
  scrollPosition: number;
  timestamp: number;
}
```

## Dependencies
- `@tanstack/react-query-persist-client` - For React Query persistence
- `localforage` (optional) - For better localStorage handling if needed

## Testing Checklist
- [ ] Scroll position restored when navigating back
- [ ] Form inputs preserved when navigating away
- [ ] Search results cached and restored
- [ ] Pagination state maintained
- [ ] Cache persists after page refresh
- [ ] Cache cleared appropriately (new search, logout)
- [ ] Multiple pages maintain independent state
- [ ] Performance is acceptable (no lag on restore)

## Future Enhancements
- IndexedDB for larger cache storage
- Cache compression for storage efficiency
- Background cache refresh
- Cache analytics and monitoring
- Selective cache invalidation

