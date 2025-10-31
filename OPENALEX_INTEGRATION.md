# OpenAlex API Integration

## Overview

Research Doomscroll now uses the **OpenAlex API** to fetch academic papers. OpenAlex is a free, open-source index of scholarly works with comprehensive coverage and rich metadata.

## Features

✅ **Polite Pool Access**: By providing your email, you get faster API access (10 requests/second vs 10 requests/minute)
✅ **Rich Metadata**: Citations, authors, venues, abstracts, and more
✅ **Topic Search**: Search papers by keywords in title and abstract
✅ **Author Search**: Find papers by author names
✅ **Combined Search**: Search by both topics and authors simultaneously
✅ **Citation Sorting**: Results sorted by citation count (most cited first)

## Setup

### 1. Add Your Email (Recommended)

To use the OpenAlex Polite Pool and get faster API access, add your email to your `.env` file:

```bash
OPENALEX_EMAIL=your-email@example.com
```

**Why provide email?**
- Without email: 10 requests/minute (slow)
- With email (Polite Pool): 10 requests/second (100x faster!)
- Your email is only used to identify you in their logs for rate limiting
- No registration or API key required

### 2. Test the Integration

1. Start the server: `.venv/bin/uvicorn app:app --reload`
2. Visit http://127.0.0.1:8000
3. Enter topics (e.g., "machine learning", "neural networks")
4. Enter authors (e.g., "Geoffrey Hinton", "Yann LeCun")
5. Click "Generate Feed"

## How It Works

### API Endpoint

The app queries: `https://api.openalex.org/works`

### Search Parameters

- **Topics**: Searches in paper titles and abstracts
- **Authors**: Searches by author display names
- **Sorting**: Results sorted by citation count (descending)
- **Pagination**: 25 papers per page by default

### Example Queries

**Topic Search:**
```
Filter: title.search:dopamine|abstract.search:dopamine
```

**Author Search:**
```
Filter: author.search:Smith
```

**Combined Search:**
```
Filter: title.search:neural networks|abstract.search:neural networks,author.search:LeCun
```

## Paper Data Structure

Each paper returned includes:

```python
{
    "paperId": "W2123456789",           # OpenAlex Work ID
    "title": "Paper Title",
    "abstract": "Full abstract text...",
    "url": "https://doi.org/...",       # DOI or landing page
    "year": 2023,
    "citationCount": 150,
    "authors": [
        {"name": "Author Name"},
        ...
    ],
    "venue": "Journal Name",
    "source": "OpenAlex",
    "tldr": "Short summary..."         # First 150 chars of abstract
}
```

## Card Display

Papers are displayed in the same card format as before, showing:

- **Title** and **Authors** (up to 3, with "+X more" for additional)
- **Year**, **Venue**, **Citation count**
- **Source badge** (OpenAlex)
- **TL;DR** (auto-generated from abstract)
- **Collapsible Abstract**
- **Like/Pass buttons**
- **External link** to full paper

## API Limits

### Free Tier (Default)
- **Rate limit**: 10 requests/minute
- **No registration**: Just use the API
- **Full access**: All features available

### Polite Pool (With Email)
- **Rate limit**: 10 requests/second (100x faster!)
- **No registration**: Just add email to `.env`
- **Full access**: All features available
- **Recommended**: Always use polite pool for better performance

## API Documentation

Full OpenAlex API docs: https://docs.openalex.org/

### Key Endpoints Used

- `/works` - Search scholarly works (papers)
- Filter by: topic, author, year, venue, citations, etc.
- Sort by: citations, publication date, relevance

### Useful Filters

```
title.search:keyword           # Search in title
abstract.search:keyword        # Search in abstract  
author.search:name             # Search by author name
publication_year:>2020         # Papers after 2020
cited_by_count:>100            # Highly cited papers
is_oa:true                     # Open access only
```

## Advantages Over Other APIs

### vs. Semantic Scholar
- ✅ No API key required
- ✅ Faster rate limits with polite pool
- ✅ More comprehensive coverage
- ✅ Open source data

### vs. bioRxiv
- ✅ Covers ALL disciplines (not just biology)
- ✅ Includes published papers (not just preprints)
- ✅ Rich citation data
- ✅ Better metadata quality

### vs. PubMed
- ✅ Covers ALL disciplines (not just medicine)
- ✅ Includes preprints and non-traditional venues
- ✅ Better API (REST vs XML)
- ✅ No API key needed

## Troubleshooting

### Slow API Responses
- **Solution**: Add your email to `.env` for Polite Pool access
- Check `OPENALEX_EMAIL` is set correctly

### No Results
- Try broader search terms
- Check spelling of author names
- Try searching by topic instead of author
- OpenAlex has very comprehensive coverage, so this is rare

### Connection Errors
- Check internet connection
- OpenAlex has 99.9%+ uptime
- API is very reliable

## Future Enhancements

Possible improvements:

1. **Advanced Filtering**
   - Filter by year range
   - Filter by citation count
   - Filter by open access status
   - Filter by venue/journal

2. **Pagination**
   - "Load More" button for additional results
   - Infinite scroll

3. **Author Disambiguation**
   - Link to OpenAlex author profiles
   - Show author H-index and stats

4. **Related Works**
   - Show papers that cite this work
   - Show papers cited by this work
   - Show related papers by topic

5. **Paper Caching**
   - Cache paper details in database
   - Display liked papers with full metadata

## Resources

- **OpenAlex Homepage**: https://openalex.org/
- **API Docs**: https://docs.openalex.org/
- **GitHub**: https://github.com/ourresearch/openalex-api-tutorials
- **Web Interface**: https://openalex.org/works (browse and explore)

## Support

OpenAlex is developed by OurResearch, a nonprofit dedicated to making research more open and accessible.

- **Twitter**: @OpenAlex_org
- **Email**: support@openalex.org
- **Status**: https://status.openalex.org/
