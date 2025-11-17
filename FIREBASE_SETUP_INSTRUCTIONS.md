# Firebase Setup Instructions

## Overview
This guide will help you set up Firebase Firestore for the Research Doomscroll application.

## Prerequisites
- Google Cloud account
- Firebase project created
- Service account key downloaded

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project"
3. Enter project name (e.g., "research-doomscroll")
4. Follow the setup wizard
5. Note your **Project ID**

## Step 2: Enable Firestore

1. In Firebase Console, go to "Firestore Database"
2. Click "Create database"
3. Choose "Start in production mode" (we'll add security rules later)
4. Select a location (choose closest to your users)
5. Click "Enable"

## Step 3: Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your Firebase project
3. Go to "IAM & Admin" > "Service Accounts"
4. Click "Create Service Account"
5. Name it (e.g., "firestore-admin")
6. Grant role: "Cloud Datastore User" or "Firebase Admin SDK Administrator Service Agent"
7. Click "Done"
8. Click on the created service account
9. Go to "Keys" tab
10. Click "Add Key" > "Create new key"
11. Choose "JSON" format
12. Download the key file
13. **Save it securely** (e.g., `firebase-service-account.json` in project root)

## Step 4: Configure Environment Variables

Add to your `.env` file:

```bash
# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id-here
FIREBASE_CREDENTIALS_PATH=./firebase-service-account.json
USE_FIREBASE=true
```

**Important**: 
- Replace `your-project-id-here` with your actual Firebase project ID
- Update the path to your service account JSON file
- Set `USE_FIREBASE=true` to enable Firebase, `false` to use PostgreSQL

## Step 5: Deploy Security Rules

1. Install Firebase CLI:
   ```bash
   npm install -g firebase-tools
   ```

2. Login to Firebase:
   ```bash
   firebase login
   ```

3. Initialize Firebase in your project:
   ```bash
   firebase init firestore
   ```
   - Select your Firebase project
   - Use existing `firestore.rules` file
   - Use existing `firestore.indexes.json` file

4. Deploy rules:
   ```bash
   firebase deploy --only firestore:rules
   ```

5. Deploy indexes:
   ```bash
   firebase deploy --only firestore:indexes
   ```

## Step 6: Test the Setup

1. Start your backend server:
   ```bash
   python run.py
   ```

2. Check logs for:
   ```
   ✅ Firebase Firestore initialized successfully
   ```

3. Try logging in with Google OAuth - user should be created in Firestore

## Step 7: Verify Data in Firestore

1. Go to Firebase Console > Firestore Database
2. You should see collections:
   - `users` - User profiles
   - `feedback` - User likes/dislikes
   - `folders` - User folders
   - `papers` - Cached paper metadata

## Troubleshooting

### Error: "Firebase initialization failed"
- Check that `FIREBASE_CREDENTIALS_PATH` points to a valid JSON file
- Verify the service account has proper permissions
- Check that `FIREBASE_PROJECT_ID` matches your Firebase project

### Error: "Permission denied"
- Verify security rules are deployed
- Check that service account has "Firebase Admin SDK Administrator" role

### Data not appearing in Firestore
- Check that `USE_FIREBASE=true` in `.env`
- Verify backend logs show Firebase initialization
- Check Firestore console for any errors

## Migration from PostgreSQL

To migrate existing data from PostgreSQL to Firestore:

1. Keep `USE_FIREBASE=false` initially
2. Run the migration script (to be created)
3. Verify data in Firestore
4. Set `USE_FIREBASE=true`
5. Test thoroughly
6. Keep PostgreSQL as backup for 30 days

## Security Notes

- **Never commit** `firebase-service-account.json` to git
- Add it to `.gitignore`
- Use environment variables for sensitive data
- Regularly rotate service account keys
- Review security rules periodically

## Next Steps

- Set up Cloud Functions for automatic stats updates
- Configure Firebase Analytics (optional)
- Set up Firebase Hosting (optional)
- Configure backup and retention policies

