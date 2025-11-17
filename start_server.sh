#!/bin/bash

# Start the backend server
# This script kills any existing server on port 8000 and starts a new one

PORT=8000
PROJECT_ROOT="/Users/samayshah/research_doomscroll"

cd "$PROJECT_ROOT"

echo "🚀 Starting Research Doomscroll Backend Server"
echo "=============================================="
echo ""

# Kill any existing process on port 8000
EXISTING_PID=$(lsof -ti:$PORT 2>/dev/null)
if [ ! -z "$EXISTING_PID" ]; then
    echo "⚠️  Found existing process on port $PORT (PID: $EXISTING_PID)"
    echo "   Killing it..."
    kill -9 $EXISTING_PID 2>/dev/null
    sleep 1
    echo "✅ Port $PORT is now free"
    echo ""
fi

# Activate virtual environment (prefer venv312 with spaCy support)
if [ -d "venv312" ]; then
    echo "✅ Using Python 3.12 environment (with spaCy support)"
    source venv312/bin/activate
elif [ -d "venv" ]; then
    echo "⚠️  Using Python 3.14 environment (spaCy not available, using regex parser)"
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "⚠️  No virtual environment found. Using system Python."
fi

# Start the server
echo "📡 Starting server on port $PORT..."
echo "   Press Ctrl+C to stop"
echo ""
python run.py

