# Fix Login Button Issue

## Status

✅ **Login button is working!** It redirects to Google OAuth.

❌ **Google OAuth error**: "Error 401: invalid_client"

## The Problem

Your `.env` file has credentials, but Google is rejecting them. This usually means:

1. **Backend needs restart** to load new `.env` values
2. **Redirect URI mismatch** in Google Console
3. **Credentials are incorrect** or not activated

## Solution

### Step 1: Restart Backend

The backend needs to be restarted to load the `.env` file:

```bash
# Stop the current backend (Ctrl+C in the terminal where it's running)
# Or kill it:
lsof -ti:8000 | xargs kill

# Then restart:
source venv/bin/activate
python3 run.py
```

### Step 2: Verify Redirect URI in Google Console

Make sure your Google OAuth redirect URI is **exactly**:
```
http://localhost:8000/api/auth/callback
```

**Important**: 
- No trailing slash
- Must be `http://localhost:8000` (not 127.0.0.1)
- Must include `/api/auth/callback`

### Step 3: Check Credentials

Verify your credentials in Google Console:
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click on your OAuth 2.0 Client ID
3. Verify:
   - Client ID matches your `.env` file
   - Client Secret matches your `.env` file
   - Redirect URI is set correctly

## After Fixing

1. Restart backend
2. Click "Login" button
3. Should redirect to Google OAuth successfully
4. After authorizing, should redirect back to app

## Quick Test

Test the login endpoint directly:
```bash
curl -L http://localhost:8000/api/auth/login
```

Should redirect to Google (not show error page).

