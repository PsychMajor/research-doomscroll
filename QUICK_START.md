# Quick Start Guide - Testing Phase 1

## Prerequisites

1. **Python 3.8+** with virtual environment activated
2. **Node.js 16+** and npm
3. **Environment variables** (see below)

## Setup Steps

### 1. Install Backend Dependencies

```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
# Required for OAuth (can be empty strings for testing without auth)
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here

# Required for sessions
SECRET_KEY=your-secret-key-here-use-python-secrets-token-hex-32

# Optional - for OpenAlex API (uses email for rate limiting)
OPENALEX_EMAIL=your-email@example.com

# Optional - PostgreSQL database URL (will use in-memory storage if not provided)
DATABASE_URL=postgresql://user:password@localhost:5432/research_doomscroll
```

**Note**: For quick testing, you can use minimal values:
- `GOOGLE_CLIENT_ID=""` and `GOOGLE_CLIENT_SECRET=""` (auth won't work but API will)
- `SECRET_KEY="dev-secret-key-change-in-production"`
- `OPENALEX_EMAIL="test@example.com"` (or your real email)

### 4. Start the Backend

```bash
# From project root
python run.py
```

Or directly:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will start on: **http://localhost:8000**

### 5. Start the Frontend (in a new terminal)

```bash
cd frontend
npm run dev
```

The frontend will start on: **http://localhost:5173**

## Testing Phase 1 Features

### 1. Test API Endpoints

Visit **http://localhost:8000/docs** to see the Swagger UI and test endpoints.

### 2. Test Frontend

Visit **http://localhost:5173** to see the React app.

**Note**: Since authentication is required for most endpoints, you'll need to:
- Set up Google OAuth credentials, OR
- Temporarily modify endpoints to allow anonymous access for testing

### 3. Test Phase 1 Features

1. **Profile API**: 
   - Should work at `/api/profile` (requires auth)
   - Test via Swagger UI at `/docs`

2. **Similar Papers**:
   - `GET /api/papers/{paper_id}/similar`
   - Try with a real OpenAlex paper ID like `W2104477830`

3. **Recommendations**:
   - `GET /api/papers/recommendations?limit=20`
   - Requires authentication and user profile

4. **Likes Page**:
   - Visit `/likes` in the frontend
   - Should show liked papers (requires auth and liked papers)

## Troubleshooting

### Backend won't start
- Check that all dependencies are installed: `pip list`
- Check for import errors in the terminal
- Verify Python version: `python --version` (should be 3.8+)

### Frontend won't start
- Check Node version: `node --version` (should be 16+)
- Delete `node_modules` and `package-lock.json`, then `npm install` again
- Check for TypeScript errors: `npm run build`

### CORS errors
- Backend CORS is configured for `localhost:5173`
- If using a different port, update `backend/main.py` CORS origins

### Authentication errors
- Most endpoints require authentication
- For testing, you can temporarily modify `require_user_id` to allow anonymous access
- Or set up Google OAuth credentials

### Database errors
- If no `DATABASE_URL` is set, the app will use in-memory storage (data lost on restart)
- For persistent storage, set up PostgreSQL and provide `DATABASE_URL`

## Next Steps

Once Phase 1 is tested and working, you can proceed to Phase 2:
- Profile-based auto-load
- Better error handling
- OpenAlex related works improvements

