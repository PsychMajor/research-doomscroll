#!/bin/bash
# Quick script to create .env file with your Google OAuth credentials

echo "🔐 Creating .env file for Research Doomscroll"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python3"
fi

# Generate secret key
SECRET_KEY=$($PYTHON_CMD -c "import secrets; print(secrets.token_urlsafe(32))")

echo "Enter your Google OAuth credentials:"
echo "(Get them from: https://console.cloud.google.com/apis/credentials)"
echo ""

read -p "GOOGLE_CLIENT_ID: " CLIENT_ID
read -p "GOOGLE_CLIENT_SECRET: " CLIENT_SECRET
read -p "Your email for OpenAlex API (or press Enter for default): " EMAIL

if [ -z "$EMAIL" ]; then
    EMAIL="samayshah@gmail.com"
fi

# Create .env file
cat > .env << EOF
# Google OAuth Credentials
GOOGLE_CLIENT_ID=$CLIENT_ID
GOOGLE_CLIENT_SECRET=$CLIENT_SECRET

# Session Secret Key (auto-generated)
SECRET_KEY=$SECRET_KEY

# OpenAlex API
OPENALEX_EMAIL=$EMAIL

# Database (optional - uses in-memory if not set)
# DATABASE_URL=postgresql://user:password@localhost:5432/research_doomscroll
EOF

echo ""
echo "✅ Created .env file!"
echo ""
echo "Next steps:"
echo "1. Start backend: source venv/bin/activate && python3 run.py"
echo "2. Start frontend: cd frontend && npm run dev"
echo "3. Visit: http://localhost:5173"

