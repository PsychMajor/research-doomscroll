# Single Page Application (SPA) Framework Implementation

## Overview
This document describes the Twitter-style SPA framework implemented for Research Doomscroll, which enables smooth navigation without full page reloads while maintaining all existing features.

## Architecture

### Core Components

#### 1. **SPAFramework Class**
The main controller that manages all SPA functionality:

```javascript
class SPAFramework {
    - viewCache: Map()  // Stores cached view states
    - currentView: string  // Current URL
    - isNavigating: boolean  // Navigation lock
}
```

**Key Methods:**
- `init()` - Initializes link interception and event listeners
- `interceptLinks()` - Captures all link clicks for SPA handling
- `navigateTo(url)` - Main navigation handler
- `saveCurrentView()` - Saves current page state to cache
- `restoreView()` - Restores previously cached view
- `fetchAndRenderView()` - Fetches and renders new view
- `handlePopState()` - Handles browser back/forward navigation

#### 2. **View Caching System**
- Uses JavaScript `Map` for in-memory view caching
- Stores HTML content, scroll position, and timestamps
- Integrated with existing sessionStorage caching for data

#### 3. **State Management**
- Preserves scroll positions between navigations
- Maintains paper lists, liked/disliked states
- Caches observer states and pagination counters

## How It Works

### Navigation Flow

1. **User clicks a link** (e.g., /likes)
   ```
   Click Event → interceptLinks() → navigateTo('/likes')
   ```

2. **Save current state**
   ```javascript
   saveCurrentView() {
       - Captures scroll position
       - Saves DOM content
       - Calls existing savePageState()
       - Stores in viewCache Map
   }
   ```

3. **Check cache**
   ```javascript
   if (viewCache.has(url)) {
       restoreView(url)  // Instant restoration
   } else {
       fetchAndRenderView(url)  // Fetch from server
   }
   ```

4. **Update history**
   ```javascript
   window.history.pushState({ url, timestamp }, '', url)
   ```

### View Restoration

When restoring a cached view:
```javascript
restoreView(url, cached) {
    1. Replace container.innerHTML with cached HTML
    2. Restore scroll position (requestAnimationFrame)
    3. Call reinitializeView()
    4. Reattach observers
    5. Mark feedback states
}
```

### Reinitialization

After each navigation, the view is reinitialized:
```javascript
reinitializeView() {
    - initializeObservers()    // Intersection Observer
    - markFeedbackStates()     // Liked/disliked UI
    - Setup scroll behavior
    - Bind event handlers
}
```

## Integration with Existing Features

### ✅ Maintained Features

1. **Infinite Scroll**
   - Observer reinitialized after each navigation
   - Progressive rendering (20 papers/batch) preserved
   - Auto-fetch on second-to-last card

2. **Caching System**
   - sessionStorage + History API (existing)
   - Added view-level caching (new)
   - Dual-layer: data cache + view cache

3. **Liked/Disliked Papers**
   - States maintained in global Sets
   - UI updated on each view restoration
   - Synced with server

4. **Pagination**
   - allPapers and renderedCount preserved
   - Deduplication by paper ID
   - Auto-fetch more papers from OpenAlex API

5. **Search Functionality**
   - Form submissions work normally
   - Search results cached
   - Query parameters in URL

### 🆕 New Features

1. **Instant Navigation**
   - No full page reloads
   - Smooth transitions
   - Loading indicators

2. **View Caching**
   - Previous views load instantly
   - Scroll position preserved
   - No server requests for cached views

3. **Browser History Integration**
   - Back/forward buttons work
   - URL updates correctly
   - History state preserved

## Helper Functions (Extracted for SPA)

### `initializeView()`
Main initialization function called on:
- Initial page load (DOMContentLoaded)
- After SPA navigation (reinitializeView)

```javascript
initializeView() {
    1. Initialize observers
    2. Load server papers
    3. Try cache restoration
    4. Mark feedback states
    5. Setup scroll behavior
}
```

### `initializeObservers()`
Sets up Intersection Observer:
- Disconnects old observer if exists
- Creates new observer with same options
- Observes all paper cards
- Handles second-to-last card detection

### `markFeedbackStates()`
Updates UI for liked/disliked papers:
- Iterates through likedPapers Set
- Finds cards by data-paper-id
- Adds 'active' class to buttons
- Applies visual transforms

### `setupScrollBehavior()`
Header hide/show on scroll:
- Monitors scroll direction
- Auto-hides header when scrolling down
- Shows header when scrolling up

## Performance Optimizations

1. **View Caching**
   - Prevents redundant server requests
   - Instant view restoration
   - Reduced bandwidth usage

2. **Lazy Observer Initialization**
   - Disconnects old observers
   - Creates fresh observers per view
   - Prevents memory leaks

3. **Request Animation Frame**
   - Smooth scroll restoration
   - Double RAF for layout completion
   - No scroll jank

4. **Navigation Lock**
   - `isNavigating` flag prevents concurrent navigations
   - Queues or skips rapid clicks
   - Maintains state integrity

## Server-Side Considerations

The server can detect SPA requests via header:
```javascript
headers: {
    'X-SPA-Request': 'true'
}
```

Future optimization: Server could return JSON instead of full HTML for SPA requests.

## Browser Compatibility

- **HTML5 History API**: IE10+, All modern browsers
- **Fetch API**: IE11+ (with polyfill), All modern browsers
- **Intersection Observer**: IE11+ (with polyfill), All modern browsers
- **Map**: IE11+, All modern browsers

## Debug Tools

### Console Logs
All SPA operations are logged with emojis:
- 🚀 Initialization
- 🔄 Navigation
- 💾 State saving
- 📂 Cache restoration
- ✅ Success
- ❌ Errors

### Browser DevTools
- Network tab: See SPA requests vs full loads
- Application tab: View sessionStorage
- Console: Real-time navigation logs

### Manual Testing
```javascript
// Check view cache
spa.viewCache

// Force navigation
spa.navigateTo('/likes')

// Clear cache
spa.clearCache()
```

## Fallback Behavior

If SPA navigation fails:
```javascript
catch (error) {
    console.error('❌ Navigation error:', error);
    // Fallback to full page load
    window.location.href = url;
}
```

This ensures the app always works, even if SPA fails.

## Future Enhancements

1. **Server-Side Optimization**
   - Return JSON for SPA requests
   - Reduce HTML overhead
   - API-first architecture

2. **Preloading**
   - Preload likely next pages
   - Hover intent detection
   - Background fetching

3. **Transitions**
   - Fade in/out animations
   - Slide transitions
   - Loading skeletons

4. **Advanced Caching**
   - LRU cache eviction
   - Cache size limits
   - IndexedDB for large data

5. **Offline Support**
   - Service Worker integration
   - Offline page caching
   - Background sync

## Comparison to Twitter

| Feature | Twitter | Research Doomscroll |
|---------|---------|---------------------|
| Link Interception | ✅ | ✅ |
| History API | ✅ | ✅ |
| View Caching | ✅ | ✅ |
| Scroll Restoration | ✅ | ✅ |
| Data Caching | IndexedDB | sessionStorage |
| React Components | ✅ | Vanilla JS |
| Service Worker | ✅ | ❌ (future) |

## Migration Impact

### Before SPA
- Every link click = full page reload
- All JavaScript re-executed
- Scroll position lost
- Cached data cleared (sometimes)

### After SPA
- Link clicks = DOM updates only
- JavaScript stays loaded
- Scroll position preserved
- Cache maintained across navigation

## Testing Checklist

- [x] Navigate from home to /likes (SPA)
- [x] Navigate back (browser back button)
- [x] Scroll position preserved
- [x] Liked papers UI correct
- [x] Infinite scroll works on both pages
- [x] External links still work (open in new tab)
- [x] Search form submissions work
- [x] Refresh page works normally

## Conclusion

The SPA framework provides a Twitter-like navigation experience while maintaining all existing features. It improves performance through view caching, eliminates page flicker, and preserves user context across navigation.
