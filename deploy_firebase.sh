#!/bin/bash

# Firebase Deployment Script
# This script deploys Firestore rules and indexes

set -e

PROJECT_ROOT="/Users/samayshah/research_doomscroll"
cd "$PROJECT_ROOT"

echo "🔥 Firebase Deployment Script"
echo "=============================="
echo ""

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI not found. Installing..."
    npm install -g firebase-tools
fi

# Check if logged in
echo "🔐 Checking Firebase authentication..."
if ! firebase projects:list &> /dev/null; then
    echo "⚠️  Not logged in to Firebase. Please run:"
    echo "   firebase login"
    echo ""
    echo "This will open a browser for authentication."
    exit 1
fi

echo "✅ Authenticated with Firebase"
echo ""

# Set the project
echo "📁 Setting Firebase project..."
firebase use research-doomscroll-2c110
echo "✅ Project set to: research-doomscroll-2c110"
echo ""

# Deploy rules
echo "📝 Deploying Firestore security rules..."
firebase deploy --only firestore:rules
echo "✅ Security rules deployed"
echo ""

# Deploy indexes
echo "📊 Deploying Firestore indexes..."
firebase deploy --only firestore:indexes
echo "✅ Indexes deployed"
echo ""

echo "🎉 Firebase deployment complete!"
echo ""
echo "Next step: Test the connection by starting your backend server:"
echo "  python run.py"
echo ""

