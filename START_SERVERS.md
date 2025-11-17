# How to Start Both Servers

## Current Status

✅ **Backend is running** on http://localhost:8000

❌ **Frontend needs to be started** in a **NEW terminal window**

## Step 1: Keep Backend Running

Your backend is already running in Terminal 1. **Don't close it!**

## Step 2: Start Frontend (New Terminal)

Open a **NEW terminal window** and run:

```bash
cd /Users/samayshah/research_doomscroll
cd frontend
npm run dev
```

Or use the helper script:

```bash
cd /Users/samayshah/research_doomscroll
./start_frontend.sh
```

## Step 3: Access the App

Once both are running:
- **Backend**: http://localhost:8000 (API)
- **Frontend**: http://localhost:5173 (Web App) ← **This is what you want!**

## Quick Commands

**Terminal 1 (Backend - already running):**
```bash
source venv/bin/activate
python3 run.py
```

**Terminal 2 (Frontend - NEW terminal):**
```bash
cd frontend
npm run dev
```

## Troubleshooting

### Frontend won't start
- Make sure you're in the `frontend` directory
- Run `npm install` if you haven't already
- Check for errors in the terminal

### Port 5173 already in use
- Kill the process: `lsof -ti:5173 | xargs kill`
- Or use a different port: `npm run dev -- --port 3000`

### Can't connect to backend
- Make sure backend is running on port 8000
- Check CORS settings in `backend/main.py`

