#!/bin/bash

# Firebase Setup Script for Research Doomscroll
# This script helps configure Firebase in your .env file

set -e

PROJECT_ROOT="/Users/samayshah/research_doomscroll"
ENV_FILE="$PROJECT_ROOT/.env"
DOWNLOADS_DIR="$HOME/Downloads"
FIREBASE_JSON_FILE="$DOWNLOADS_DIR/research-doomscroll-6a80920bebcc.json"
TARGET_JSON_FILE="$PROJECT_ROOT/firebase-service-account.json"

echo "🔥 Firebase Setup Script"
echo "========================"
echo ""

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "⚠️  .env file not found. Creating it..."
    touch "$ENV_FILE"
fi

# Check if Firebase JSON file exists in Downloads
if [ ! -f "$FIREBASE_JSON_FILE" ]; then
    echo "❌ Firebase service account JSON file not found at:"
    echo "   $FIREBASE_JSON_FILE"
    echo ""
    read -p "Enter the full path to your Firebase service account JSON file: " FIREBASE_JSON_FILE
    if [ ! -f "$FIREBASE_JSON_FILE" ]; then
        echo "❌ File not found: $FIREBASE_JSON_FILE"
        exit 1
    fi
fi

echo "✅ Found Firebase service account file: $FIREBASE_JSON_FILE"
echo ""

# Extract project ID from JSON file
PROJECT_ID=$(grep -o '"project_id"[[:space:]]*:[[:space:]]*"[^"]*"' "$FIREBASE_JSON_FILE" | head -1 | sed 's/.*"project_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')

if [ -z "$PROJECT_ID" ]; then
    echo "⚠️  Could not extract project_id from JSON file"
    read -p "Enter your Firebase Project ID: " PROJECT_ID
else
    echo "✅ Extracted Project ID: $PROJECT_ID"
fi

echo ""

# Copy JSON file to project root
echo "📁 Copying service account file to project root..."
cp "$FIREBASE_JSON_FILE" "$TARGET_JSON_FILE"
echo "✅ Copied to: $TARGET_JSON_FILE"
echo ""

# Update .env file
echo "📝 Updating .env file..."

# Backup .env file
cp "$ENV_FILE" "$ENV_FILE.backup"
echo "✅ Created backup: $ENV_FILE.backup"

# Remove existing Firebase config if present
sed -i.bak '/^FIREBASE_PROJECT_ID=/d' "$ENV_FILE" 2>/dev/null || sed -i '' '/^FIREBASE_PROJECT_ID=/d' "$ENV_FILE"
sed -i.bak '/^FIREBASE_CREDENTIALS_PATH=/d' "$ENV_FILE" 2>/dev/null || sed -i '' '/^FIREBASE_CREDENTIALS_PATH=/d' "$ENV_FILE"
sed -i.bak '/^USE_FIREBASE=/d' "$ENV_FILE" 2>/dev/null || sed -i '' '/^USE_FIREBASE=/d' "$ENV_FILE"
rm -f "$ENV_FILE.bak" 2>/dev/null || true

# Add Firebase configuration
echo "" >> "$ENV_FILE"
echo "# Firebase Configuration" >> "$ENV_FILE"
echo "FIREBASE_PROJECT_ID=$PROJECT_ID" >> "$ENV_FILE"
echo "FIREBASE_CREDENTIALS_PATH=./firebase-service-account.json" >> "$ENV_FILE"
echo "USE_FIREBASE=true" >> "$ENV_FILE"

echo "✅ Added Firebase configuration to .env"
echo ""

# Update .gitignore to ensure JSON file is not committed
if [ -f "$PROJECT_ROOT/.gitignore" ]; then
    if ! grep -q "firebase-service-account.json" "$PROJECT_ROOT/.gitignore"; then
        echo "" >> "$PROJECT_ROOT/.gitignore"
        echo "# Firebase service account key" >> "$PROJECT_ROOT/.gitignore"
        echo "firebase-service-account.json" >> "$PROJECT_ROOT/.gitignore"
        echo "✅ Added firebase-service-account.json to .gitignore"
    fi
fi

echo ""
echo "🎉 Firebase setup complete!"
echo ""
echo "Configuration added to .env:"
echo "  FIREBASE_PROJECT_ID=$PROJECT_ID"
echo "  FIREBASE_CREDENTIALS_PATH=./firebase-service-account.json"
echo "  USE_FIREBASE=true"
echo ""
echo "Next steps:"
echo "  1. Review your .env file to ensure all settings are correct"
echo "  2. Deploy Firestore security rules: firebase deploy --only firestore:rules"
echo "  3. Deploy Firestore indexes: firebase deploy --only firestore:indexes"
echo "  4. Start your backend server to test Firebase connection"
echo ""

