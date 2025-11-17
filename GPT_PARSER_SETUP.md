# GPT-4o-mini Query Parser Setup

## Overview

The query parser now uses **GPT-4o-mini** from OpenAI for accurate entity extraction from search queries. This provides better accuracy than local models for detecting authors, institutions, years, and keywords.

## Setup

### 1. Install OpenAI Library

```bash
pip install openai
```

### 2. Set OpenAI API Key

You need to set your OpenAI API key. You can do this in two ways:

**Option 1: Environment Variable (Recommended)**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

**Option 2: .env File**
Add to your `.env` file in the project root:
```
OPENAI_API_KEY=your-api-key-here
```

Or add to `backend/config.py` settings:
```python
openai_api_key: str = "your-api-key-here"
```

## How It Works

1. **GPT-4o-mini Model**: Uses OpenAI's GPT-4o-mini model for entity extraction
   - Fast and cost-effective
   - High accuracy for named entity recognition
   - Structured JSON output

2. **Entity Extraction**:
   - **Keywords/Topics**: Research topics and subject areas
   - **Authors**: Person names (normalized to proper case)
   - **Years**: Publication years, ranges, and relative years
   - **Institutions**: Universities and research organizations

3. **Response Format**: Returns structured JSON with arrays for each entity type

## API Endpoint

The parser is available at:
```
GET /api/papers/parse-query?q=your+search+query
```

**Example:**
```bash
curl "http://localhost:8000/api/papers/parse-query?q=machine%20learning%20by%20John%20Smith%20in%202020%20at%20MIT"
```

**Response:**
```json
{
  "keywords": ["machine learning"],
  "authors": ["John Smith"],
  "years": ["2020"],
  "institutions": ["MIT"]
}
```

## Cost

GPT-4o-mini is very cost-effective:
- ~$0.15 per 1M input tokens
- ~$0.60 per 1M output tokens
- Typical query parsing uses < 100 tokens total

## Fallback

If the OpenAI API is unavailable or the API key is not set, the endpoint will return empty arrays for all entities, allowing the UI to continue functioning (just without highlighting).

