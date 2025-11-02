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
MEMORY_PAPERS = {}  # paper_id -> paper_data

async def init_db():
    """Initialize database connection pool and create tables"""
    global pool
    
    if not DATABASE_URL:
        print("⚠️  No DATABASE_URL found, using in-memory storage")
        return
    
    print("🔄 Initializing database connection...")
    try:
        # Create connection pool
        pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
        print("✅ Database connection pool created")
        
        # Create tables
        async with pool.acquire() as conn:
            print("🔄 Creating/verifying database tables...")
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
            
            # Papers table - stores paper metadata
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS papers (
                    paper_id TEXT PRIMARY KEY,
                    title TEXT,
                    authors JSONB,
                    abstract TEXT,
                    year INTEGER,
                    venue TEXT,
                    citation_count INTEGER,
                    url TEXT,
                    source TEXT,
                    tldr TEXT,
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
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_papers_paper_id ON papers(paper_id)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback(user_id)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_feedback_paper_id ON feedback(paper_id)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_cache_key ON paper_cache(cache_key, source)')
            print("✅ Tables and indexes created/verified")
            
            # Migration: Add columns if they don't exist
            print("🔄 Running database migrations...")
            migration_success = True
            try:
                # Check and add user_id to profiles
                user_id_exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='profiles' AND column_name='user_id'
                    )
                """)
                if not user_id_exists:
                    await conn.execute('''
                        ALTER TABLE profiles 
                        ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
                    ''')
                    print("✅ Added user_id column to profiles")
                
                # Check and add user_id to feedback
                feedback_user_id_exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='feedback' AND column_name='user_id'
                    )
                """)
                if not feedback_user_id_exists:
                    await conn.execute('''
                        ALTER TABLE feedback 
                        ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
                    ''')
                    print("✅ Added user_id column to feedback")
                
                # Check and add folders to profiles
                folders_exists = await conn.fetchval("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='profiles' AND column_name='folders'
                    )
                """)
                if not folders_exists:
                    await conn.execute('''
                        ALTER TABLE profiles 
                        ADD COLUMN folders JSONB DEFAULT '[]'::jsonb
                    ''')
                    print("✅ Added folders column to profiles")
                    
                    # Update existing rows to have default Likes folder
                    await conn.execute("""
                        UPDATE profiles 
                        SET folders = '[{"name": "Likes", "id": "likes"}]'::jsonb
                        WHERE folders IS NULL OR folders::text = '[]'
                    """)
                    print("✅ Initialized folders with default Likes folder")
                else:
                    print("✅ Folders column already exists")
                
                print("✅ Database migrations completed successfully")
            except Exception as migration_error:
                migration_success = False
                print(f"❌ Migration error: {migration_error}")
                import traceback
                traceback.print_exc()
                print("⚠️  WARNING: Migrations failed! Application may not work correctly.")
                print("⚠️  Please run: python migrate_db.py")
            
        if migration_success:
            print("✅ Database initialized successfully")
        else:
            print("⚠️  Database initialized with migration errors")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("   Falling back to in-memory storage")
        import traceback
        traceback.print_exc()

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
            profile = MEMORY_PROFILES[user_id]
            print(f"📂 Loaded profile from in-memory storage for user {user_id}")
            if 'folders' in profile:
                print(f"   Folders: {[f['name'] for f in profile.get('folders', [])]}")
            return profile
        print(f"📂 No profile found in memory for user {user_id}, returning defaults")
        return {"topics": [], "authors": [], "folders": [{"name": "Likes", "id": "likes"}]}
    
    try:
        async with pool.acquire() as conn:
            if user_id:
                row = await conn.fetchrow(
                    'SELECT topics, authors, folders FROM profiles WHERE user_id = $1 ORDER BY updated_at DESC LIMIT 1',
                    user_id
                )
            else:
                row = await conn.fetchrow('SELECT topics, authors, folders FROM profiles ORDER BY updated_at DESC LIMIT 1')
            
            if row:
                folders = json.loads(row['folders']) if row['folders'] else [{"name": "Likes", "id": "likes"}]
                # Ensure default Likes folder exists
                if not any(f['id'] == 'likes' for f in folders):
                    folders.insert(0, {"name": "Likes", "id": "likes"})
                print(f"📂 Loaded profile from PostgreSQL database for user {user_id}")
                print(f"   Folders: {[f['name'] for f in folders]}")
                return {
                    "topics": json.loads(row['topics']) if row['topics'] else [],
                    "authors": json.loads(row['authors']) if row['authors'] else [],
                    "folders": folders
                }
            else:
                print(f"📂 No profile found in database for user {user_id}, returning defaults")
    except Exception as e:
        print(f"⚠️  Error loading profile: {e}")
        import traceback
        traceback.print_exc()
    
    return {"topics": [], "authors": [], "folders": [{"name": "Likes", "id": "likes"}]}

async def save_profile(topics_list: List[str], authors_list: List[str], user_id: Optional[int] = None):
    """Save user profile to database"""
    if not pool:
        # Use in-memory storage
        if user_id:
            if user_id not in MEMORY_PROFILES:
                MEMORY_PROFILES[user_id] = {"topics": [], "authors": [], "folders": [{"name": "Likes", "id": "likes"}]}
            MEMORY_PROFILES[user_id]["topics"] = topics_list
            MEMORY_PROFILES[user_id]["authors"] = authors_list
            # Preserve existing folders
            print(f"✅ Profile (topics/authors) saved to in-memory storage for user {user_id}")
        return
    
    try:
        async with pool.acquire() as conn:
            # Check if profile exists to preserve folders
            existing = await conn.fetchrow(
                'SELECT folders FROM profiles WHERE user_id = $1 ORDER BY updated_at DESC LIMIT 1',
                user_id
            )
            
            if existing:
                # Update ALL rows for this user, preserve folders
                folders = existing['folders'] if existing['folders'] else json.dumps([{"name": "Likes", "id": "likes"}])
                await conn.execute('''
                    UPDATE profiles 
                    SET topics = $1, authors = $2, folders = $3, updated_at = NOW()
                    WHERE user_id = $4
                ''', json.dumps(topics_list), json.dumps(authors_list), folders, user_id)
                print(f"✅ Profile (topics/authors) updated in PostgreSQL database for user {user_id}")
                print(f"   Preserved existing folders")
            else:
                # Create new profile
                await conn.execute('''
                    INSERT INTO profiles (user_id, topics, authors, folders)
                    VALUES ($1, $2, $3, $4)
                ''', user_id, json.dumps(topics_list), json.dumps(authors_list), json.dumps([{"name": "Likes", "id": "likes"}]))
                print(f"✅ New profile created in PostgreSQL database for user {user_id}")
    except Exception as e:
        print(f"⚠️  Error saving profile: {e}")
        import traceback
        traceback.print_exc()

async def save_folders(folders_list: List[Dict], user_id: Optional[int] = None):
    """Save user folders to database"""
    if not pool:
        # Use in-memory storage
        if user_id:
            if user_id not in MEMORY_PROFILES:
                MEMORY_PROFILES[user_id] = {"topics": [], "authors": [], "folders": []}
            MEMORY_PROFILES[user_id]["folders"] = folders_list
            print(f"✅ Folders saved to in-memory storage for user {user_id}")
            print(f"   Current folders: {[f['name'] for f in folders_list]}")
        return
    
    try:
        async with pool.acquire() as conn:
            # Check if profile exists
            profile = await conn.fetchrow(
                'SELECT id, topics, authors FROM profiles WHERE user_id = $1 ORDER BY updated_at DESC LIMIT 1',
                user_id
            )
            
            if profile:
                # Update ALL rows for this user (not just one)
                await conn.execute('''
                    UPDATE profiles 
                    SET folders = $1, updated_at = NOW()
                    WHERE user_id = $2
                ''', json.dumps(folders_list), user_id)
                print(f"✅ Folders updated in PostgreSQL database for user {user_id}")
                print(f"   Updated all profile rows for this user")
                print(f"   Current folders: {[f['name'] for f in folders_list]}")
            else:
                # Create new profile with folders
                await conn.execute('''
                    INSERT INTO profiles (user_id, topics, authors, folders)
                    VALUES ($1, $2, $3, $4)
                ''', user_id, json.dumps([]), json.dumps([]), json.dumps(folders_list))
                print(f"✅ New profile created in PostgreSQL database for user {user_id}")
                print(f"   Current folders: {[f['name'] for f in folders_list]}")
    except Exception as e:
        print(f"⚠️  Error saving folders: {e}")
        import traceback
        traceback.print_exc()

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

# Paper storage functions
async def save_paper(paper_data: Dict):
    """Save paper metadata to database"""
    paper_id = paper_data.get('paperId')
    if not paper_id:
        return
    
    if not pool:
        # Use in-memory storage
        MEMORY_PAPERS[paper_id] = paper_data
        return
    
    try:
        async with pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO papers (paper_id, title, authors, abstract, year, venue, citation_count, url, source, tldr)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ON CONFLICT (paper_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    authors = EXCLUDED.authors,
                    abstract = EXCLUDED.abstract,
                    year = EXCLUDED.year,
                    venue = EXCLUDED.venue,
                    citation_count = EXCLUDED.citation_count,
                    url = EXCLUDED.url,
                    source = EXCLUDED.source,
                    tldr = EXCLUDED.tldr,
                    updated_at = NOW()
            ''', 
                paper_id,
                paper_data.get('title'),
                json.dumps(paper_data.get('authors', [])),
                paper_data.get('abstract'),
                paper_data.get('year'),
                paper_data.get('venue'),
                paper_data.get('citationCount', 0),
                paper_data.get('url'),
                paper_data.get('source'),
                paper_data.get('tldr')
            )
    except Exception as e:
        print(f"⚠️  Error saving paper: {e}")

async def get_paper(paper_id: str) -> Optional[Dict]:
    """Get paper metadata from database"""
    if not pool:
        # Use in-memory storage
        return MEMORY_PAPERS.get(paper_id)
    
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                'SELECT * FROM papers WHERE paper_id = $1',
                paper_id
            )
            if row:
                paper = dict(row)
                # Convert JSONB back to list
                if paper.get('authors'):
                    paper['authors'] = json.loads(paper['authors']) if isinstance(paper['authors'], str) else paper['authors']
                # Rename fields to match expected format
                paper['paperId'] = paper['paper_id']
                paper['citationCount'] = paper['citation_count']
                return paper
    except Exception as e:
        print(f"⚠️  Error getting paper: {e}")
    
    return None

async def get_papers_by_ids(paper_ids: List[str]) -> List[Dict]:
    """Get multiple papers by their IDs"""
    if not pool:
        # Use in-memory storage
        return [MEMORY_PAPERS[pid] for pid in paper_ids if pid in MEMORY_PAPERS]
    
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                'SELECT * FROM papers WHERE paper_id = ANY($1) ORDER BY created_at DESC',
                paper_ids
            )
            papers = []
            for row in rows:
                paper = dict(row)
                # Convert JSONB back to list
                if paper.get('authors'):
                    paper['authors'] = json.loads(paper['authors']) if isinstance(paper['authors'], str) else paper['authors']
                # Rename fields to match expected format
                paper['paperId'] = paper['paper_id']
                paper['citationCount'] = paper['citation_count']
                papers.append(paper)
            return papers
    except Exception as e:
        print(f"⚠️  Error getting papers: {e}")
    
    return []

# Convenience methods for like/dislike functionality
async def like_paper(paper_id: str, user_id: Optional[int] = None):
    """Mark a paper as liked"""
    await save_feedback(paper_id, 'liked', user_id)

async def unlike_paper(paper_id: str, user_id: Optional[int] = None):
    """Remove like from a paper"""
    await delete_feedback(paper_id, user_id)

async def dislike_paper(paper_id: str, user_id: Optional[int] = None):
    """Mark a paper as disliked"""
    await save_feedback(paper_id, 'disliked', user_id)

async def undislike_paper(paper_id: str, user_id: Optional[int] = None):
    """Remove dislike from a paper"""
    await delete_feedback(paper_id, user_id)

async def clear_feedback(user_id: Optional[int] = None):
    """Clear all feedback for a user"""
    await clear_all_feedback(action=None, user_id=user_id)

async def clear_liked(user_id: Optional[int] = None):
    """Clear all liked papers for a user"""
    await clear_all_feedback(action='liked', user_id=user_id)

async def clear_disliked(user_id: Optional[int] = None):
    """Clear all disliked papers for a user"""
    await clear_all_feedback(action='disliked', user_id=user_id)

