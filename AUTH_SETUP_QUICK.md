# Quick Auth Setup Guide 🚀

## Option 1: Automated Setup (Recommended)

Run the setup script:

```bash
python setup_auth.py
```

This will:
- Generate a secure `SECRET_KEY`
- Prompt you for Google OAuth credentials
- Create/update your `.env` file

## Option 2: Manual Setup

### Step 1: Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Go to **"APIs & Services" > "Credentials"**
4. Click **"+ CREATE CREDENTIALS" > "OAuth client ID"**
5. Configure OAuth consent screen if prompted:
   - App name: `Research Doomscroll`
   - User support email: Your email
6. Create OAuth client:
   - Type: **Web application**
   - Name: `Research Doomscroll Web Client`
   - **Authorized redirect URIs**: 
     ```
     http://localhost:8000/api/auth/callback
     ```
7. Copy your **Client ID** and **Client Secret**

### Step 2: Create .env File

Create a `.env` file in the project root:

```bash
# Generate secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Create `.env` with:

```env
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
SECRET_KEY=paste-generated-secret-key-here
OPENALEX_EMAIL=your-email@example.com
```

### Step 3: Test

1. Start backend: `python run.py`
2. Start frontend: `cd frontend && npm run dev`
3. Visit: http://localhost:5173
4. Click "Login" and authorize with Google
5. You should be logged in! ✅

## Troubleshooting

### "redirect_uri_mismatch"
- Make sure redirect URI in Google Console is exactly: `http://localhost:8000/api/auth/callback`
- No trailing slash!

### "invalid_client"
- Check `.env` file has correct values
- No quotes around values
- Restart backend after changing `.env`

### Can't login
- Check backend is running on port 8000
- Check frontend is running on port 5173
- Check browser console for errors
- Verify CORS is configured (should be automatic)

## Full Documentation

See `GOOGLE_OAUTH_SETUP.md` for detailed step-by-step instructions.

## Next Steps

Once auth is working:
1. ✅ Test login/logout
2. ✅ Test Phase 1 features
3. ✅ Ready for testing!

