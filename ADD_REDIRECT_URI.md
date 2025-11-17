# How to Add Redirect URI to Google Cloud Console

## The Problem

Google is showing: **"Error 400: redirect_uri_mismatch"**

This means the redirect URI `http://localhost:8000/api/auth/callback` is not registered in your Google OAuth client.

## Step-by-Step Fix

### 1. Open Google Cloud Console

Go to: **https://console.cloud.google.com/apis/credentials**

### 2. Find Your OAuth Client

- Look for the OAuth 2.0 Client ID that matches your Client ID:
  - `498889079675-b6f733983hc7iritvnv6a9k87bi7o7q6.apps.googleusercontent.com`
- **Click on it** to open the edit page

### 3. Add the Redirect URI

Scroll down to the **"Authorized redirect URIs"** section.

Click **"+ ADD URI"** and enter:

```
http://localhost:8000/api/auth/callback
```

**⚠️ IMPORTANT:**
- Must be **exactly** this (no trailing slash)
- Must use `http://` (not `https://`)
- Must use `localhost:8000` (not `127.0.0.1:8000`)
- Must include `/api/auth/callback`

### 4. Save

Click **"SAVE"** at the bottom of the page.

### 5. Wait a Few Seconds

Google may take 10-30 seconds to propagate the change.

### 6. Test Again

1. Go to: http://localhost:5173
2. Click "Login" button
3. Should now work! ✅

## Common Mistakes

❌ **Wrong:** `http://localhost:8000/api/auth/callback/` (trailing slash)
❌ **Wrong:** `http://127.0.0.1:8000/api/auth/callback` (wrong hostname)
❌ **Wrong:** `https://localhost:8000/api/auth/callback` (wrong protocol)
❌ **Wrong:** `http://localhost:8000/callback` (missing `/api/auth`)

✅ **Correct:** `http://localhost:8000/api/auth/callback`

## Still Not Working?

1. **Double-check the URI** - Copy/paste it exactly
2. **Wait longer** - Sometimes takes up to 5 minutes
3. **Clear browser cache** - Try incognito mode
4. **Check you're editing the right OAuth client** - Make sure the Client ID matches

## Screenshot Guide

The "Authorized redirect URIs" section should look like this after adding:

```
Authorized redirect URIs
┌─────────────────────────────────────────────────────────┐
│ http://localhost:8000/api/auth/callback                 │
└─────────────────────────────────────────────────────────┘
[+ ADD URI]
```

