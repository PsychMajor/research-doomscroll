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
            # User profiles table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS profiles (
                    id SERIAL PRIMARY KEY,
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
                    paper_id TEXT UNIQUE NOT NULL,
                    action TEXT NOT NULL, -- 'liked' or 'disliked'
                    created_at TIMESTAMP DEFAULT NOW()
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

# Profile functions
async def load_profile() -> Dict:
    """Load user profile from database"""
    if not pool:
        return {"topics": [], "authors": []}
    
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow('SELECT topics, authors FROM profiles ORDER BY updated_at DESC LIMIT 1')
            if row:
                return {
                    "topics": json.loads(row['topics']) if row['topics'] else [],
                    "authors": json.loads(row['authors']) if row['authors'] else []
                }
    except Exception as e:
        print(f"⚠️  Error loading profile: {e}")
    
    return {"topics": [], "authors": []}

async def save_profile(topics_list: List[str], authors_list: List[str]):
    """Save user profile to database"""
    if not pool:
        return
    
    try:
        async with pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO profiles (topics, authors)
                VALUES ($1, $2)
            ''', json.dumps(topics_list), json.dumps(authors_list))
        print("✅ Profile saved to database")
    except Exception as e:
        print(f"⚠️  Error saving profile: {e}")

# Feedback functions
async def load_feedback() -> Dict:
    """Load user feedback from database"""
    if not pool:
        return {"liked": [], "disliked": []}
    
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch('SELECT paper_id, action FROM feedback')
            liked = [row['paper_id'] for row in rows if row['action'] == 'liked']
            disliked = [row['paper_id'] for row in rows if row['action'] == 'disliked']
            return {"liked": liked, "disliked": disliked}
    except Exception as e:
        print(f"⚠️  Error loading feedback: {e}")
    
    return {"liked": [], "disliked": []}

async def save_feedback(paper_id: str, action: str):
    """Save feedback for a paper"""
    if not pool:
        return
    
    try:
        async with pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO feedback (paper_id, action)
                VALUES ($1, $2)
                ON CONFLICT (paper_id) DO UPDATE SET action = $2
            ''', paper_id, action)
    except Exception as e:
        print(f"⚠️  Error saving feedback: {e}")

async def delete_feedback(paper_id: str):
    """Delete feedback for a paper"""
    if not pool:
        return
    
    try:
        async with pool.acquire() as conn:
            await conn.execute('DELETE FROM feedback WHERE paper_id = $1', paper_id)
    except Exception as e:
        print(f"⚠️  Error deleting feedback: {e}")

async def clear_all_feedback(action: Optional[str] = None):
    """Clear all feedback or specific action"""
    if not pool:
        return
    
    try:
        async with pool.acquire() as conn:
            if action:
                await conn.execute('DELETE FROM feedback WHERE action = $1', action)
            else:
                await conn.execute('DELETE FROM feedback')
        print(f"✅ Cleared {'all' if not action else action} feedback from database")
    except Exception as e:
        print(f"⚠️  Error clearing feedback: {e}")
