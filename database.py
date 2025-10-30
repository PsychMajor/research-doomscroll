"""
Database module for persistent storage using PostgreSQL
Falls back to in-memory storage if database is not available
"""
import os
import json
from typing import Dict, List, Optional
import asyncpg

DATABASE_URL = os.environ.get("DATABASE_URL")

# Connection pool
pool = None

# In-memory storage for when database is not available
MEMORY_USERS = {}  # email -> {id, email, name, picture_url}
MEMORY_USER_ID_COUNTER = 1
MEMORY_PROFILES = {}  # user_id -> {topics: [], authors: []}
MEMORY_FEEDBACK = {}  # user_id -> {paper_id: action}

async def init_db():
    """Initialize database connection pool and create tables"""
    global pool
    
    if not DATABASE_URL:
        print("⚠️  No DATABASE_URL found, using in-memory storage")
        return
    
    try:
        # Create connection pool
        pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
        
        # Create tables
        async with pool.acquire() as conn:
            # Users table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255),
                    picture_url TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    last_login TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # User profiles table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS profiles (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    topics TEXT,
                    authors TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # User feedback table (likes/dislikes)
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    paper_id TEXT NOT NULL,
                    action TEXT NOT NULL, -- 'liked' or 'disliked'
                    created_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(user_id, paper_id)
                )
            ''')
            
            # Paper cache table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS paper_cache (
                    id SERIAL PRIMARY KEY,
                    cache_key TEXT NOT NULL,
                    paper_data JSONB NOT NULL,
                    source TEXT NOT NULL, -- 'semantic_scholar', 'biorxiv', 'mixed'
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Create indexes
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback(user_id)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_feedback_paper_id ON feedback(paper_id)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_cache_key ON paper_cache(cache_key, source)')
            
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"⚠️  Database initialization failed: {e}")
        print("   Falling back to in-memory storage")

async def close_db():
    """Close database connection pool"""
    global pool
    if pool:
        await pool.close()

# User functions
async def create_or_update_user(email: str, name: str = None, picture_url: str = None) -> Optional[int]:
    """Create or update user and return user_id"""
    global MEMORY_USER_ID_COUNTER
    
    if not pool:
        # Use in-memory storage
        if email not in MEMORY_USERS:
            MEMORY_USERS[email] = {
                'id': MEMORY_USER_ID_COUNTER,
                'email': email,
                'name': name,
                'picture_url': picture_url
            }
            user_id = MEMORY_USER_ID_COUNTER
            MEMORY_USER_ID_COUNTER += 1
        else:
            # Update existing user
            MEMORY_USERS[email]['name'] = name
            MEMORY_USERS[email]['picture_url'] = picture_url
            user_id = MEMORY_USERS[email]['id']
        
        print(f"✅ In-memory user created/updated: {email} (ID: {user_id})")
        return user_id
    
    try:
        async with pool.acquire() as conn:
            # Upsert user
            result = await conn.fetchrow('''
                INSERT INTO users (email, name, picture_url, last_login)
                VALUES ($1, $2, $3, NOW())
                ON CONFLICT (email) 
                DO UPDATE SET 
                    name = EXCLUDED.name, 
                    picture_url = EXCLUDED.picture_url, 
                    last_login = NOW()
                RETURNING id
            ''', email, name, picture_url)
            return result['id'] if result else None
    except Exception as e:
        print(f"⚠️  Error creating/updating user: {e}")
        return None

async def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    if not pool:
        # Use in-memory storage
        for user in MEMORY_USERS.values():
            if user['id'] == user_id:
                return user
        return None
    
    if not user_id:
        return None
    
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                'SELECT id, email, name, picture_url FROM users WHERE id = $1',
                user_id
            )
            if row:
                return dict(row)
    except Exception as e:
        print(f"⚠️  Error getting user: {e}")
    
    return None

# Profile functions
async def load_profile(user_id: Optional[int] = None) -> Dict:
    """Load user profile from database"""
    if not pool:
        # Use in-memory storage
        if user_id and user_id in MEMORY_PROFILES:
            return MEMORY_PROFILES[user_id]
        return {"topics": [], "authors": []}
    
    try:
        async with pool.acquire() as conn:
            if user_id:
                row = await conn.fetchrow(
                    'SELECT topics, authors FROM profiles WHERE user_id = $1 ORDER BY updated_at DESC LIMIT 1',
                    user_id
                )
            else:
                row = await conn.fetchrow('SELECT topics, authors FROM profiles ORDER BY updated_at DESC LIMIT 1')
            
            if row:
                return {
                    "topics": json.loads(row['topics']) if row['topics'] else [],
                    "authors": json.loads(row['authors']) if row['authors'] else []
                }
    except Exception as e:
        print(f"⚠️  Error loading profile: {e}")
    
    return {"topics": [], "authors": []}

async def save_profile(topics_list: List[str], authors_list: List[str], user_id: Optional[int] = None):
    """Save user profile to database"""
    if not pool:
        # Use in-memory storage
        if user_id:
            MEMORY_PROFILES[user_id] = {
                "topics": topics_list,
                "authors": authors_list
            }
            print(f"✅ Profile saved to memory for user {user_id}")
        return
    
    try:
        async with pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO profiles (user_id, topics, authors)
                VALUES ($1, $2, $3)
            ''', user_id, json.dumps(topics_list), json.dumps(authors_list))
        print("✅ Profile saved to database")
    except Exception as e:
        print(f"⚠️  Error saving profile: {e}")

# Feedback functions
async def load_feedback(user_id: Optional[int] = None) -> Dict:
    """Load user feedback from database"""
    if not pool:
        # Use in-memory storage
        if user_id and user_id in MEMORY_FEEDBACK:
            user_feedback = MEMORY_FEEDBACK[user_id]
            liked = [pid for pid, action in user_feedback.items() if action == 'liked']
            disliked = [pid for pid, action in user_feedback.items() if action == 'disliked']
            return {"liked": liked, "disliked": disliked}
        return {"liked": [], "disliked": []}
    
    try:
        async with pool.acquire() as conn:
            if user_id:
                rows = await conn.fetch(
                    'SELECT paper_id, action FROM feedback WHERE user_id = $1',
                    user_id
                )
            else:
                rows = await conn.fetch('SELECT paper_id, action FROM feedback')
            
            liked = [row['paper_id'] for row in rows if row['action'] == 'liked']
            disliked = [row['paper_id'] for row in rows if row['action'] == 'disliked']
            return {"liked": liked, "disliked": disliked}
    except Exception as e:
        print(f"⚠️  Error loading feedback: {e}")
    
    return {"liked": [], "disliked": []}

async def save_feedback(paper_id: str, action: str, user_id: Optional[int] = None):
    """Save feedback for a paper"""
    if not pool:
        # Use in-memory storage
        if user_id:
            if user_id not in MEMORY_FEEDBACK:
                MEMORY_FEEDBACK[user_id] = {}
            MEMORY_FEEDBACK[user_id][paper_id] = action
            print(f"✅ Feedback saved to memory: user {user_id}, paper {paper_id}, action {action}")
        return
    
    try:
        async with pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO feedback (user_id, paper_id, action)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id, paper_id) DO UPDATE SET action = $3
            ''', user_id, paper_id, action)
    except Exception as e:
        print(f"⚠️  Error saving feedback: {e}")

async def delete_feedback(paper_id: str, user_id: Optional[int] = None):
    """Delete feedback for a paper"""
    if not pool:
        # Use in-memory storage
        if user_id and user_id in MEMORY_FEEDBACK and paper_id in MEMORY_FEEDBACK[user_id]:
            del MEMORY_FEEDBACK[user_id][paper_id]
            print(f"✅ Feedback deleted from memory: user {user_id}, paper {paper_id}")
        return
    
    try:
        async with pool.acquire() as conn:
            if user_id:
                await conn.execute(
                    'DELETE FROM feedback WHERE paper_id = $1 AND user_id = $2',
                    paper_id, user_id
                )
            else:
                await conn.execute('DELETE FROM feedback WHERE paper_id = $1', paper_id)
    except Exception as e:
        print(f"⚠️  Error deleting feedback: {e}")

async def clear_all_feedback(action: Optional[str] = None, user_id: Optional[int] = None):
    """Clear all feedback or specific action"""
    if not pool:
        # Use in-memory storage
        if user_id and user_id in MEMORY_FEEDBACK:
            if action:
                # Remove only specific action
                MEMORY_FEEDBACK[user_id] = {
                    pid: act for pid, act in MEMORY_FEEDBACK[user_id].items() 
                    if act != action
                }
            else:
                # Clear all feedback for user
                MEMORY_FEEDBACK[user_id] = {}
            print(f"✅ Cleared {'all' if not action else action} feedback from memory for user {user_id}")
        return
    
    try:
        async with pool.acquire() as conn:
            if user_id:
                if action:
                    await conn.execute(
                        'DELETE FROM feedback WHERE action = $1 AND user_id = $2',
                        action, user_id
                    )
                else:
                    await conn.execute('DELETE FROM feedback WHERE user_id = $1', user_id)
            else:
                if action:
                    await conn.execute('DELETE FROM feedback WHERE action = $1', action)
                else:
                    await conn.execute('DELETE FROM feedback')
        print(f"✅ Cleared {'all' if not action else action} feedback from database")
    except Exception as e:
        print(f"⚠️  Error clearing feedback: {e}")
