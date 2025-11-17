# Google OAuth Setup Guide

This guide will walk you through setting up Google OAuth authentication for Research Doomscroll.

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click **"New Project"**
4. Enter project name: `Research Doomscroll` (or any name you prefer)
5. Click **"Create"**
6. Wait for the project to be created and select it

## Step 2: Enable Google+ API

1. In the Google Cloud Console, go to **"APIs & Services" > "Library"**
2. Search for **"Google+ API"** or **"Google Identity"**
3. Click on **"Google+ API"** or **"Google Identity Services API"**
4. Click **"Enable"**

**Note**: Google+ API is being deprecated, but the OAuth 2.0 endpoints still work. Alternatively, you can use:
- **"Google Identity Services API"** (newer)
- The OAuth endpoints work with either

## Step 3: Create OAuth 2.0 Credentials

1. Go to **"APIs & Services" > "Credentials"**
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"OAuth client ID"**
4. If prompted, configure the OAuth consent screen first (see Step 4)
5. Select **"Web application"** as the application type
6. Give it a name: `Research Doomscroll Web Client`

## Step 4: Configure OAuth Consent Screen

If you haven't configured it yet:

1. Go to **"APIs & Services" > "OAuth consent screen"**
2. Select **"External"** (unless you have a Google Workspace account)
3. Click **"Create"**
4. Fill in the required fields:
   - **App name**: `Research Doomscroll`
   - **User support email**: Your email
   - **Developer contact information**: Your email
5. Click **"Save and Continue"**
6. On **"Scopes"** page, click **"Save and Continue"** (we'll use default scopes)
7. On **"Test users"** page, add your email if using "External" mode
8. Click **"Save and Continue"**
9. Review and click **"Back to Dashboard"**

## Step 5: Configure Authorized Redirect URIs

When creating the OAuth client ID (Step 3), you'll see a form. Fill in:

**Authorized JavaScript origins:**
```
http://localhost:8000
http://localhost:5173
http://127.0.0.1:8000
http://127.0.0.1:5173
```

**Authorized redirect URIs:**
```
http://localhost:8000/api/auth/callback
http://127.0.0.1:8000/api/auth/callback
```

**Important**: 
- For production, add your production URLs
- The redirect URI must match exactly what your backend sends
- Our backend uses: `{base_url}/api/auth/callback`

## Step 6: Get Your Credentials

After creating the OAuth client:

1. You'll see a popup with your **Client ID** and **Client Secret**
2. **Copy both values** - you'll need them for the `.env` file
3. If you missed them, go to **"Credentials"** and click on your OAuth client to view them

## Step 7: Create .env File

Create a `.env` file in the project root directory:

```bash
# In the project root
touch .env
```

Add the following content (replace with your actual values):

```env
# Google OAuth Credentials
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here

# Session Secret Key (generate a random string)
SECRET_KEY=your-secret-key-here-use-python-secrets-token-hex-32

# OpenAlex API (your email for rate limiting)
OPENALEX_EMAIL=your-email@example.com

# Database (optional - uses in-memory if not set)
# DATABASE_URL=postgresql://user:password@localhost:5432/research_doomscroll
```

## Step 8: Generate Secret Key

Generate a secure secret key for sessions:

```bash
# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or using OpenSSL
openssl rand -hex 32
```

Copy the output and use it as your `SECRET_KEY` in the `.env` file.

## Step 9: Verify Setup

1. Make sure your `.env` file is in the project root
2. Restart your backend server:
   ```bash
   python run.py
   ```
3. Check the console - you should see "✅ Database initialized"
4. Visit: http://localhost:8000/docs
5. Try the `/api/auth/login` endpoint or visit: http://localhost:8000/api/auth/login

## Troubleshooting

### "redirect_uri_mismatch" Error

**Problem**: Google says the redirect URI doesn't match.

**Solution**:
1. Check that your redirect URI in Google Console is exactly: `http://localhost:8000/api/auth/callback`
2. Make sure you're accessing the backend on `localhost:8000` (not a different port)
3. If using a different port, update both:
   - Google Console redirect URI
   - Backend CORS settings in `backend/main.py`

### "invalid_client" Error

**Problem**: Client ID or secret is incorrect.

**Solution**:
1. Double-check your `.env` file
2. Make sure there are no extra spaces or quotes
3. Restart the backend server after changing `.env`

### OAuth Consent Screen Issues

**Problem**: "This app isn't verified" warning.

**Solution**:
- For development, this is normal
- Click "Advanced" > "Go to Research Doomscroll (unsafe)" to proceed
- For production, you'll need to verify your app with Google

### Session Not Persisting

**Problem**: Login works but session is lost on refresh.

**Solution**:
1. Check that `SECRET_KEY` is set in `.env`
2. Make sure cookies are enabled in your browser
3. Check browser console for CORS errors
4. Verify `allow_credentials=True` in CORS middleware

## Testing the Auth Flow

1. **Start Backend**:
   ```bash
   python run.py
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test Login**:
   - Visit: http://localhost:5173
   - Click "Login" button
   - You should be redirected to Google
   - After authorizing, you'll be redirected back
   - You should be logged in!

4. **Verify Session**:
   - Check browser DevTools > Application > Cookies
   - You should see a session cookie for `localhost:8000`
   - Visit: http://localhost:8000/api/auth/status
   - Should return `{"authenticated": true, "user": {...}}`

## Quick Reference

### Environment Variables Needed

```env
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
SECRET_KEY=xxx (32+ character random string)
OPENALEX_EMAIL=your-email@example.com
```

### Important URLs

- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **Login**: http://localhost:8000/api/auth/login
- **Callback**: http://localhost:8000/api/auth/callback
- **Status**: http://localhost:8000/api/auth/status

### Google Console Links

- [Google Cloud Console](https://console.cloud.google.com/)
- [Credentials](https://console.cloud.google.com/apis/credentials)
- [OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)

## Next Steps

Once authentication is working:

1. ✅ Test login/logout flow
2. ✅ Test protected endpoints (profile, feedback, etc.)
3. ✅ Test Phase 1 features:
   - Search papers
   - Like papers
   - View likes page
   - Get recommendations
   - Get similar papers

Happy testing! 🎉

