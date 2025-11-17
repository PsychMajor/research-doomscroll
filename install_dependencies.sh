#!/bin/bash

# Script to install all required dependencies for the backend

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Installing Backend Dependencies${NC}"
echo "=================================="
echo ""

# Get the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment (prefer venv312)
if [ -d "venv312" ]; then
    echo -e "${YELLOW}Using Python 3.12 environment${NC}"
    source venv312/bin/activate
elif [ -d "venv" ]; then
    echo -e "${YELLOW}Using Python 3.14 environment${NC}"
    source venv/bin/activate
else
    echo "❌ No virtual environment found!"
    exit 1
fi

echo ""
echo "Installing core dependencies..."
pip install --quiet fastapi uvicorn pydantic pydantic-settings

echo "Installing authentication dependencies..."
pip install --quiet authlib python-jose passlib bcrypt

echo "Installing database dependencies..."
pip install --quiet sqlalchemy asyncpg psycopg2-binary

echo "Installing Firebase dependencies..."
pip install --quiet firebase-admin

echo "Installing NLP dependencies..."
pip install --quiet nltk openai

echo "Installing other dependencies..."
pip install --quiet httpx python-multipart starlette itsdangerous jinja2

echo ""
echo -e "${GREEN}✅ All dependencies installed!${NC}"
echo ""
echo "You can now start the server with: ./start_server.sh"

