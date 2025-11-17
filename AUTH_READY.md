# Authentication Setup Complete! ✅

## What I Fixed

1. ✅ **Fixed Auth API Endpoints** - Updated frontend to use `/api/auth/*` routes
2. ✅ **Fixed Login/Logout Redirects** - Now redirects to frontend (localhost:5173)
3. ✅ **Created Setup Guides**:
   - `GOOGLE_OAUTH_SETUP.md` - Detailed step-by-step guide
   - `AUTH_SETUP_QUICK.md` - Quick reference
   - `setup_auth.py` - Automated setup script

## Quick Start (3 Steps)

### 1. Run Setup Script

```bash
python setup_auth.py
```

This will:
- Generate a secure `SECRET_KEY`
- Prompt you for Google OAuth credentials
- Create your `.env` file

### 2. Get Google OAuth Credentials

If you don't have them yet:

1. Go to: https://console.cloud.google.com/apis/credentials
2. Create OAuth 2.0 Client ID
3. Set redirect URI: `http://localhost:8000/api/auth/callback`
4. Copy Client ID and Secret
5. Add them to `.env` (or run `setup_auth.py` again)

**See `GOOGLE_OAUTH_SETUP.md` for detailed instructions.**

### 3. Start Servers

**Terminal 1 - Backend:**
```bash
python run.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 4. Test!

1. Visit: http://localhost:5173
2. Click "Login"
3. Authorize with Google
4. You should be logged in! 🎉

## Files Created/Updated

### New Files
- `GOOGLE_OAUTH_SETUP.md` - Complete OAuth setup guide
- `AUTH_SETUP_QUICK.md` - Quick reference
- `setup_auth.py` - Automated setup helper

### Updated Files
- `frontend/src/api/auth.ts` - Fixed API endpoints
- `backend/routers/auth.py` - Fixed redirect URLs

## Environment Variables Needed

Your `.env` file should have:

```env
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
SECRET_KEY=xxx (32+ character random string)
OPENALEX_EMAIL=your-email@example.com
```

## Testing Checklist

Once auth is set up:

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can click "Login" button
- [ ] Redirected to Google OAuth
- [ ] Can authorize with Google
- [ ] Redirected back to app
- [ ] User info appears in header
- [ ] Can access protected endpoints
- [ ] Can logout

## Troubleshooting

### Common Issues

**"redirect_uri_mismatch"**
- Check redirect URI in Google Console is exactly: `http://localhost:8000/api/auth/callback`
- No trailing slash!

**"invalid_client"**
- Verify `.env` file has correct values
- Restart backend after changing `.env`

**Can't see login button**
- Check frontend is running on port 5173
- Check browser console for errors
- Verify auth status endpoint works: http://localhost:8000/api/auth/status

## Next Steps

Once authentication is working:

1. ✅ Test Phase 1 features:
   - Search papers
   - Like papers
   - View likes page
   - Get recommendations
   - Get similar papers

2. ✅ Ready for full testing!

## Need Help?

- **Detailed OAuth Setup**: See `GOOGLE_OAUTH_SETUP.md`
- **Quick Reference**: See `AUTH_SETUP_QUICK.md`
- **General Setup**: See `QUICK_START.md`

Happy testing! 🚀

