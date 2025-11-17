# Quick Check: Environment Variables

## The Issue

The login button **IS working**, but Google OAuth is showing:
- **Error 401: invalid_client**
- **"The OAuth client was not found"**

This means your Google OAuth credentials are not set in the `.env` file.

## Quick Fix

1. **Check if `.env` exists**:
   ```bash
   ls -la .env
   ```

2. **If it doesn't exist, create it**:
   ```bash
   # Activate venv
   source venv/bin/activate
   
   # Generate secret key
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Create `.env` file** with your Google OAuth credentials:
   ```env
   GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret-here
   SECRET_KEY=paste-generated-secret-key-here
   OPENALEX_EMAIL=your-email@example.com
   ```

4. **Restart the backend** after creating/updating `.env`:
   ```bash
   # Stop current backend (Ctrl+C)
   # Then restart:
   source venv/bin/activate
   python3 run.py
   ```

## Or Use the Helper Script

```bash
source venv/bin/activate
./create_env.sh
```

This will prompt you for your credentials and create the `.env` file.

## Verify It's Working

After setting up `.env` and restarting:
1. Click "Login" button
2. Should redirect to Google OAuth (not show error)
3. After authorizing, should redirect back to app

