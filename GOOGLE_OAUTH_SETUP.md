# Google OAuth Setup Guide

Follow these steps to add Google authentication to your Research Doomscroll app:

## 1. Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth 2.0 Client ID**
5. If prompted, configure the OAuth consent screen first:
   - Choose "External" for user type
   - Fill in the required fields (App name, support email, etc.)
   - Add your email to test users if in testing mode
   - Save and continue

## 2. Configure OAuth Client

1. Select **Web application** as the application type
2. Add **Authorized JavaScript origins**:
   - `http://localhost:8000` (for local development)
   - `https://research-doomscroll.onrender.com` (for production)
3. Add **Authorized redirect URIs**:
   - `http://localhost:8000/auth/callback`
   - `https://research-doomscroll.onrender.com/auth/callback`
4. Click **Create**
5. Copy the **Client ID** and **Client Secret**

## 3. Set Environment Variables

### For Local Development:

Create a `.env` file in the project root:

```bash
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
SECRET_KEY=your-secret-key-here
DATABASE_URL=your-postgres-url
```

Generate a secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### For Render.com Deployment:

1. Go to your Render dashboard
2. Select your web service
3. Go to **Environment** tab
4. Add the following environment variables:
   - `GOOGLE_CLIENT_ID` = your Google client ID
   - `GOOGLE_CLIENT_SECRET` = your Google client secret
   - `SECRET_KEY` = your generated secret key (keep it secret!)
   - `DATABASE_URL` = (should already be set if you have PostgreSQL)

## 4. Install Required Packages

```bash
pip install authlib httpx itsdangerous
```

Or update from requirements.txt:
```bash
pip install -r requirements.txt
```

## 5. Update Database

The database schema will be automatically updated when you start the app. It will create:
- `users` table for storing user profiles
- Update `profiles` and `feedback` tables with `user_id` foreign keys

## 6. Test the Authentication

1. Start your app:
   ```bash
   uvicorn app:app --reload
   ```

2. Navigate to `http://localhost:8000`

3. Click "Sign in with Google"

4. You should be redirected to Google's login page

5. After successful login, you'll be redirected back to your app

## Security Notes

- Never commit `.env` file or expose your `GOOGLE_CLIENT_SECRET`
- Use a strong, random `SECRET_KEY` in production
- Keep the `SECRET_KEY` secure - it protects user sessions
- In production, ensure your domain is added to authorized origins/redirect URIs

## Troubleshooting

### "redirect_uri_mismatch" Error
- Make sure the redirect URI in Google Console exactly matches your app's callback URL
- Check for trailing slashes and http vs https

### "unauthorized_client" Error
- Verify your OAuth consent screen is properly configured
- Add test users if your app is in testing mode

### Users Not Being Saved
- Check that `DATABASE_URL` is set correctly
- Verify database connectivity
- Check server logs for error messages

## Features

Once authentication is set up:
- Each user gets their own profile and preferences
- Likes and dislikes are saved per user
- Data is isolated between users
- Users can log out and log back in to access their data
