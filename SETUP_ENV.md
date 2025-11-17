# Quick Environment Setup

## Option 1: Use the Script (Easiest)

Since you already have your Google OAuth keys, run:

```bash
# Activate virtual environment first
source venv/bin/activate

# Run the setup script
./create_env.sh
```

It will prompt you for:
- GOOGLE_CLIENT_ID
- GOOGLE_CLIENT_SECRET  
- Your email (optional, defaults to samayshah@gmail.com)

## Option 2: Manual Setup

Create a `.env` file in the project root:

```bash
# Activate virtual environment
source venv/bin/activate

# Generate secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Then create `.env` file with:

```env
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
SECRET_KEY=paste-generated-secret-key-here
OPENALEX_EMAIL=your-email@example.com
```

## Option 3: Use Python Setup Script

```bash
# Activate virtual environment
source venv/bin/activate

# Run setup script
python3 setup_auth.py
```

## Important Notes

1. **Always activate venv first**: `source venv/bin/activate`
2. **Use python3**: On macOS, use `python3` not `python`
3. **Redirect URI**: Make sure your Google OAuth redirect URI is set to:
   ```
   http://localhost:8000/api/auth/callback
   ```

## After Creating .env

1. **Start Backend**:
   ```bash
   source venv/bin/activate
   python3 run.py
   ```

2. **Start Frontend** (new terminal):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test**: Visit http://localhost:5173 and click "Login"

