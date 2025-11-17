# Firebase Deployment Guide

## ✅ Completed Steps

1. ✅ Firebase CLI installed
2. ✅ Configuration files created:
   - `.firebaserc` - Project configuration
   - `firebase.json` - Firestore rules and indexes configuration
3. ✅ Service account file in place
4. ✅ `.env` file configured

## 🔐 Step 1: Login to Firebase

You need to authenticate with Firebase CLI. Run:

```bash
firebase login
```

This will:
- Open your browser
- Ask you to sign in with your Google account
- Grant permissions to Firebase CLI
- Complete authentication

**Note:** Use the same Google account that owns the Firebase project.

## 🚀 Step 2: Deploy Rules and Indexes

After logging in, run the deployment script:

```bash
./deploy_firebase.sh
```

Or manually:

```bash
# Set the project
firebase use research-doomscroll-2c110

# Deploy security rules
firebase deploy --only firestore:rules

# Deploy indexes
firebase deploy --only firestore:indexes
```

## ✅ Step 3: Verify Deployment

After deployment, you should see:
- ✅ Security rules deployed successfully
- ✅ Indexes deployed successfully

You can verify in the Firebase Console:
- Go to Firestore Database > Rules tab
- Go to Firestore Database > Indexes tab

## 🧪 Step 4: Test Connection

Start your backend server:

```bash
python run.py
```

Look for this message in the logs:
```
✅ Firebase Firestore initialized successfully
```

## 🔧 Troubleshooting

### Error: "Failed to authenticate"
- Make sure you ran `firebase login`
- Use the same Google account that owns the project

### Error: "Permission denied"
- The service account needs proper permissions
- Or use `firebase login` with your personal account

### Error: "Project not found"
- Verify the project ID: `research-doomscroll-2c110`
- Make sure you have access to the project

## 📝 Quick Reference

```bash
# Login
firebase login

# Set project
firebase use research-doomscroll-2c110

# Deploy rules
firebase deploy --only firestore:rules

# Deploy indexes
firebase deploy --only firestore:indexes

# Check status
firebase projects:list
```

