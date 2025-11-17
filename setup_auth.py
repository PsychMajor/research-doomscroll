#!/usr/bin/env python3
# Run with: python3 setup_auth.py (or activate venv first)
"""
Helper script to set up authentication environment variables
"""
import secrets
import os

def generate_secret_key():
    """Generate a secure secret key for sessions"""
    return secrets.token_urlsafe(32)

def create_env_file():
    """Create or update .env file with authentication settings"""
    env_file = '.env'
    
    # Check if .env already exists
    existing_vars = {}
    if os.path.exists(env_file):
        print(f"📄 Found existing {env_file} file")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    existing_vars[key.strip()] = value.strip()
    
    # Generate secret key if not present
    if 'SECRET_KEY' not in existing_vars or not existing_vars['SECRET_KEY']:
        secret_key = generate_secret_key()
        existing_vars['SECRET_KEY'] = secret_key
        print(f"✅ Generated new SECRET_KEY")
    else:
        print(f"ℹ️  Using existing SECRET_KEY")
    
    # Prompt for Google OAuth credentials
    print("\n" + "="*60)
    print("Google OAuth Setup")
    print("="*60)
    print("Get your credentials from: https://console.cloud.google.com/apis/credentials")
    print("See GOOGLE_OAUTH_SETUP.md for detailed instructions\n")
    
    if 'GOOGLE_CLIENT_ID' not in existing_vars or not existing_vars['GOOGLE_CLIENT_ID']:
        client_id = input("Enter GOOGLE_CLIENT_ID (or press Enter to skip): ").strip()
        if client_id:
            existing_vars['GOOGLE_CLIENT_ID'] = client_id
    else:
        print(f"ℹ️  Using existing GOOGLE_CLIENT_ID")
    
    if 'GOOGLE_CLIENT_SECRET' not in existing_vars or not existing_vars['GOOGLE_CLIENT_SECRET']:
        client_secret = input("Enter GOOGLE_CLIENT_SECRET (or press Enter to skip): ").strip()
        if client_secret:
            existing_vars['GOOGLE_CLIENT_SECRET'] = client_secret
    else:
        print(f"ℹ️  Using existing GOOGLE_CLIENT_SECRET")
    
    # Set default OpenAlex email if not present
    if 'OPENALEX_EMAIL' not in existing_vars or not existing_vars['OPENALEX_EMAIL']:
        email = input("Enter your email for OpenAlex API (or press Enter to skip): ").strip()
        if email:
            existing_vars['OPENALEX_EMAIL'] = email
        else:
            existing_vars['OPENALEX_EMAIL'] = 'samayshah@gmail.com'
            print(f"ℹ️  Using default OPENALEX_EMAIL: samayshah@gmail.com")
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write("# Google OAuth Credentials\n")
        f.write("# Get these from: https://console.cloud.google.com/apis/credentials\n")
        f.write(f"GOOGLE_CLIENT_ID={existing_vars.get('GOOGLE_CLIENT_ID', '')}\n")
        f.write(f"GOOGLE_CLIENT_SECRET={existing_vars.get('GOOGLE_CLIENT_SECRET', '')}\n")
        f.write("\n")
        f.write("# Session Secret Key\n")
        f.write(f"SECRET_KEY={existing_vars.get('SECRET_KEY', '')}\n")
        f.write("\n")
        f.write("# OpenAlex API\n")
        f.write(f"OPENALEX_EMAIL={existing_vars.get('OPENALEX_EMAIL', 'samayshah@gmail.com')}\n")
        f.write("\n")
        f.write("# Database (optional - uses in-memory if not set)\n")
        if 'DATABASE_URL' in existing_vars:
            f.write(f"# DATABASE_URL={existing_vars['DATABASE_URL']}\n")
        else:
            f.write("# DATABASE_URL=postgresql://user:password@localhost:5432/research_doomscroll\n")
    
    print(f"\n✅ Created/updated {env_file} file")
    print("\nNext steps:")
    print("1. Make sure GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are set")
    print("2. See GOOGLE_OAUTH_SETUP.md for detailed OAuth setup instructions")
    print("3. Start the backend: python run.py")
    print("4. Start the frontend: cd frontend && npm run dev")

if __name__ == '__main__':
    try:
        create_env_file()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")

