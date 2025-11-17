# Fix Redirect URI Mismatch

## ✅ Progress

1. ✅ Backend is loading credentials from `.env` correctly
2. ✅ Login button is working
3. ✅ OAuth flow is initiating
4. ❌ **Redirect URI mismatch** - needs to be added to Google Console

## The Problem

Google is rejecting the OAuth request because the redirect URI `http://localhost:8000/api/auth/callback` is not registered in your Google OAuth client configuration.

## Solution

### Step 1: Go to Google Cloud Console

1. Open: https://console.cloud.google.com/apis/credentials
2. Click on your OAuth 2.0 Client ID (the one with your Client ID)

### Step 2: Add Redirect URI

In the "Authorized redirect URIs" section, add:

```
http://localhost:8000/api/auth/callback
```

**Important:**
- Must be **exactly** this (no trailing slash)
- Must use `http://localhost:8000` (not `127.0.0.1`)
- Must include `/api/auth/callback`

### Step 3: Save

Click "Save" at the bottom of the page.

### Step 4: Test

1. Go back to http://localhost:5173
2. Click "Login" button
3. Should now redirect to Google OAuth successfully!

## For Production

When deploying, you'll need to add your production redirect URI as well, e.g.:
```
https://yourdomain.com/api/auth/callback
```

