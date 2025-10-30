# Google Authentication Implementation

## What Was Added

✅ **Complete Google OAuth 2.0 authentication** is now integrated into your Research Doomscroll app!

### Features Implemented:

1. **User Authentication**
   - Sign in with Google button in the header
   - OAuth 2.0 secure authentication flow
   - User avatar and name display when logged in
   - Logout functionality

2. **User-Specific Data**
   - Each user gets their own isolated profile
   - Likes and dislikes are saved per user account
   - Topic preferences are saved per user
   - Data persists across sessions

3. **Database Updates**
   - New `users` table to store Google account info
   - Updated `profiles` table with `user_id` foreign key
   - Updated `feedback` table with `user_id` foreign key
   - Automatic schema migration on startup

4. **Security**
   - Session-based authentication using SECRET_KEY
   - User data completely isolated per Google account
   - Secure OAuth token handling
   - No passwords stored (delegated to Google)

## Files Modified:

- `app.py` - Added OAuth routes and user context
- `database.py` - Added user management functions
- `requirements.txt` - Added authlib, httpx, itsdangerous
- `templates/index.html` - Added login UI in header
- `static/style.css` - Added authentication UI styles

## Files Created:

- `GOOGLE_OAUTH_SETUP.md` - Complete setup guide
- `.env.example` - Environment variable template

## Next Steps:

### 1. Set Up Google OAuth Credentials

Follow the detailed guide in `GOOGLE_OAUTH_SETUP.md` to:
1. Create OAuth credentials in Google Cloud Console
2. Get your Client ID and Client Secret
3. Configure redirect URIs

### 2. Add Environment Variables

**For Local Development:**
Create a `.env` file:
```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
DATABASE_URL=your-postgres-url
```

**For Render.com:**
Add these in the Environment tab:
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `SECRET_KEY`

### 3. Test Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
uvicorn app:app --reload

# Visit http://localhost:8000
# Click "Sign in with Google"
```

### 4. Deploy to Render

1. Push changes to GitHub (already done ✅)
2. Add environment variables in Render dashboard
3. Redeploy your app
4. Test authentication on live site

## How It Works:

1. **User clicks "Sign in with Google"**
   - Redirected to Google's login page
   - User authenticates with their Google account

2. **Google redirects back to `/auth/callback`**
   - User info (email, name, picture) is retrieved
   - User record created/updated in database
   - Session is created with user_id

3. **User is now logged in**
   - All profile/feedback operations use their user_id
   - Data is automatically filtered to show only their data
   - Avatar and name displayed in header

4. **User clicks "Logout"**
   - Session is cleared
   - Redirected to homepage (shows public view)

## Benefits:

- ✅ No password management needed
- ✅ Secure authentication via Google
- ✅ Each user gets their own personalized experience
- ✅ Data privacy - users can only see their own data
- ✅ Easy to use - one-click Google sign-in
- ✅ Persistent sessions - stays logged in

## Without OAuth Setup:

If you don't set up Google OAuth (missing CLIENT_ID/SECRET):
- The "Sign in with Google" button will show an error page
- The app still works but data is not user-specific
- All users share the same profile/feedback (like before)

## Support:

Questions? Check `GOOGLE_OAUTH_SETUP.md` for detailed instructions and troubleshooting tips!
