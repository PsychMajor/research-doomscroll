# Research Doomscroll 🔬

A Twitter-like interface for infinite scrolling through research papers, powered by Semantic Scholar API.

## Features

### 🎯 Personalized Research Profile
- **Save Your Interests**: Create a profile with your research topics and favorite authors
- **Curated Feed**: Get a personalized feed of papers based on your saved profile
- **Auto-Load**: Your feed automatically loads when you visit the app
- **Easy Updates**: Modify your profile anytime to refine your feed

### 📱 Twitter-Style UI
- Beautiful dark theme with card-based layout
- Paper cards showing: title, authors, year, citations, abstract, and link
- Responsive design (works great on mobile!)
- Smooth animations and hover effects

### 🔍 Smart Search
- Search by research topics/keywords
- Filter by specific authors
- Combine multiple topics and authors
- Real-time feed generation

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Set up your Semantic Scholar API key for higher rate limits:
```bash
export SEMANTIC_SCHOLAR_API_KEY="your-api-key-here"
```

Get your free API key at: https://www.semanticscholar.org/product/api#api-key-form

## Usage

1. Start the server:
```bash
uvicorn app:app --reload
```

2. Open your browser to: http://127.0.0.1:8000

3. Enter your research interests:
   - **Topics**: e.g., "machine learning, neural networks, computer vision"
   - **Authors**: e.g., "Geoffrey Hinton, Yann LeCun" (optional)

4. Click "💾 Save Profile & Generate Feed"

5. Your profile is saved locally and will auto-load next time!

## Profile Management

- **Save Profile**: Your topics and authors are saved to `profile.json`
- **Auto-Load**: Visit `/` to see your personalized feed instantly
- **Update**: Just enter new interests and click save again
- **Clear**: Click "🗑️ Clear Profile" to start over

## API Endpoints

- `GET /` - Main feed interface
- `POST /profile/save` - Save your research profile
- `GET /profile` - Get current profile as JSON
- `POST /profile/clear` - Clear saved profile
- `GET /api/papers` - Get papers as JSON

## Rate Limits

- **Free tier**: Limited requests per minute
- **With API key**: Much higher limits
- If you hit the rate limit, wait a few minutes or add an API key

## Tech Stack

- **Backend**: FastAPI + Python
- **Frontend**: HTML + CSS (Twitter-inspired design)
- **API**: Semantic Scholar
- **Storage**: Local JSON file

## Project Structure

```
research_doomscroll/
├── app.py              # FastAPI backend
├── requirements.txt    # Python dependencies
├── profile.json        # Your saved profile (auto-generated)
├── templates/
│   └── index.html     # Main UI template
└── static/
    └── style.css      # Twitter-style CSS
```

## Tips

- Start with broad topics, then refine based on results
- Author search is optional but helps narrow results
- Refresh the page to generate a new feed
- Check the "Active filters" section to see your current search

Enjoy your research doomscroll! 📚✨
