# Cache Testing Guide

## ⚠️ IMPORTANT: Where to Find Logs

**The caching logs appear in your BROWSER CONSOLE, not the terminal!**

- **Browser Console**: Press `F12` (or `Cmd+Option+I` on Mac) to open Developer Tools
- **Terminal**: Only shows server-side logs (API calls, database operations)
- **Cache Logs**: All the `💾 CACHE SAVED`, `📂 CACHE FOUND`, etc. appear in the **browser console**

## What Was Added

I've implemented a comprehensive localStorage caching system that preserves your search results, scroll position, and interaction state when navigating between pages.

## How to Test

1. **Start Server** (if not already running):
   ```bash
   .venv/bin/python -m uvicorn app:app --reload
   ```

2. **Open Browser Console** (F12 or Cmd+Option+I) ← **THIS IS WHERE YOU'LL SEE THE CACHE LOGS**
   - Keep console open to see all cache logging messages
   - Look for colorful emoji icons like 💾 📂 🔍 ✨ 🗑️

3. **Test the Cache**:

### Test 1: Basic Caching & Restoration
1. Do a search (e.g., author: "brian kobilka", sort by: "Recency")
2. Scroll down through several papers
3. Like a few papers (this triggers cache save)
4. Expand some abstracts (this also triggers cache save)
5. **Watch console for**: `💾 CACHE SAVED` messages
6. Click on "Likes" in the navigation (navigate away)
7. Click "Search" in the navigation (return to search page)
8. **Watch console for**: 
   - `🚀 PAGE LOAD - Checking for cache...`
   - `📂 CACHE FOUND` (shows cached data details)
   - `🔍 SEARCH COMPARISON` (shows if search params match)
   - `� RESTORE DECISION` (shows cache vs server comparison)
   - `�🔄 RESTORING CACHE` (shows restoration in progress)
   - `✨ RESTORE COMPLETE` (shows how many papers restored)
   - `📍 Scroll position restored` (shows scroll position)
9. **Result**: You should see ALL your papers (not just first 25), at the exact scroll position, with likes and expanded abstracts preserved! ✨

### Test 2: Cache Persists Through Same Search
1. With papers loaded, click the "Search" nav button
2. Click "Generate Feed" button WITHOUT changing topics/authors
3. **Watch console for**: `📌 Same search parameters, keeping cache`
4. **Result**: Papers should restore from cache instantly (no API call)

### Test 3: New Search Clears Cache
1. With papers loaded, click the "Search" nav button  
2. Change the author or topics field
3. Click "Generate Feed"
4. **Watch console for**: `🗑️ CACHE CLEARED - New search initiated`
5. **Result**: New results should appear (fresh API call)

### Test 3: Cache Auto-Save
1. Load papers and interact (like, scroll, expand abstracts)
2. **Watch console every 30 seconds for**: `💾 CACHE SAVED`
3. **Watch console when scrolling stops for**: `💾 CACHE SAVED`
4. **Watch console when liking/disliking for**: `💾 CACHE SAVED`

## Console Log Key

- `🚀 PAGE LOAD` - Page is loading, checking for cache
- `📂 CACHE FOUND` - Valid cache detected in localStorage
- `📂 No cache found` - No cached data available
- `💾 CACHE SAVED` - Data successfully saved to cache
- `🔍 SEARCH COMPARISON` - Comparing cached search params with current
- `🔄 RESTORING CACHE` - Starting cache restoration
- `✨ RESTORE COMPLETE` - Cache successfully restored
- `📍 Scroll position restored` - Scroll position set
- `🗑️ CACHE CLEARED` - Cache deleted (new search)
- `⚠️ Cannot restore` - Problem preventing restoration
- `❌ Error` - Something went wrong

## What Should Happen

### When It Works ✅
1. You search for papers
2. You scroll, like, expand abstracts
3. You click "Likes" page
4. You click "Search" to return
5. **Result**: Papers instantly reappear at your exact scroll position with all abstracts still expanded and likes preserved

### When It Doesn't Work ❌
Look for these console messages:
- `⚠️ Cannot restore: No papers in cached state`
- `🔄 Different search parameters detected, NOT restoring cache`
- `📄 Using fresh server data instead of cache`
- `❌ Error loading page state`

## Cache Details

- **Storage**: Browser localStorage (survives page reload)
- **Key**: `research_doomscroll_cache`
- **Version**: `1.0`
- **Expiry**: 24 hours
- **What's Cached**:
  - All paper data (title, authors, abstract, etc.)
  - Scroll position
  - Expanded abstracts
  - Liked/disliked papers
  - Search parameters (topics, authors)

## Troubleshooting

If cache isn't working, check console for:

1. **No save messages?**
   - Make sure you have papers loaded
   - Try liking a paper (should trigger save)
   - Wait 30 seconds (auto-save)

2. **No restore messages?**
   - Cache might have expired (24 hours)
   - Search params might not match
   - Check if `CURRENT_TOPICS` and `CURRENT_AUTHORS` match

3. **Cache found but not restored?**
   - Check `SEARCH COMPARISON` log
   - Make sure you're not doing a fresh search
   - Check if server sent new papers

## Manual Cache Inspection

Open browser console and run:
```javascript
// See what's cached
const cache = localStorage.getItem('research_doomscroll_cache');
const state = JSON.parse(cache);
console.log(state);

// Check cache age
console.log('Cache age (minutes):', Math.round((Date.now() - state.timestamp) / 1000 / 60));

// Clear cache manually
localStorage.removeItem('research_doomscroll_cache');
console.log('Cache cleared');
```

## Expected Behavior

The cache should:
- ✅ Save automatically every 30 seconds
- ✅ Save when you scroll (1 second after stopping)
- ✅ Save when you like/dislike papers
- ✅ Save when toggling abstracts
- ✅ Save before leaving page
- ✅ Restore when returning from another page (same search)
- ✅ Restore when clicking "Generate Feed" with same parameters
- ✅ Clear ONLY when search parameters actually change (topics or authors)
- ✅ Expire after 24 hours
- ✅ Prefer cache over fresh server data (keeps all loaded papers, not just first 25)

## Key Behavior Changes

**Before**: Cache cleared every time you clicked "Generate Feed"
**After**: Cache only clears when search parameters (topics/authors) actually change

This means:
- Navigate to /likes and back → **Restores full cache** ✅
- Click "Generate Feed" with same params → **Restores cache** ✅  
- Click "Generate Feed" with new params → **Clears cache, fresh search** ✅
- Load more papers → **Cache grows** ✅
- Return from another page → **See all papers you loaded** ✅
