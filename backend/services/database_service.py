"""
Database Service

Handles all database operations for users, profiles, feedback, and papers.
Falls back to in-memory storage if database is not available.
"""

import json
from typing import Dict, List, Optional
import asyncpg
from ..config import get_settings
from ..models.paper import Paper
from ..models.user import User, UserProfile
from ..models.folder import Folder
from ..models.feedback import FeedbackResponse


class DatabaseService:
    """Service for database operations"""
    
    def __init__(self):
        self.settings = get_settings()
        self.pool: Optional[asyncpg.Pool] = None
        
        # In-memory storage fallback
        self.memory_users = {}
        self.memory_user_id_counter = 1
        self.memory_profiles = {}
        self.memory_feedback = {}
        self.memory_papers = {}
    
    async def init_db(self):
        """Initialize database connection pool and create tables"""
        if not self.settings.database_url:
            print("⚠️  No DATABASE_URL found, using in-memory storage")
            return
        
        print("🔄 Initializing database connection...")
        try:
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                self.settings.database_url, 
                min_size=1, 
                max_size=5
            )
            print("✅ Database connection pool created")
            
            # Create tables
            await self._create_tables()
            print("✅ Database initialized successfully")
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            print("   Falling back to in-memory storage")
            import traceback
            traceback.print_exc()
    
    async def close_db(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
    
    async def _create_tables(self):
        """Create database tables if they don't exist"""
        if not self.pool:
            return
        
        async with self.pool.acquire() as conn:
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
                    folders JSONB DEFAULT '[]'::jsonb,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Papers table
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
                    doi TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # User feedback table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    paper_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(user_id, paper_id)
                )
            ''')
            
            # Create indexes
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_papers_paper_id ON papers(paper_id)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback(user_id)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_feedback_paper_id ON feedback(paper_id)')
            
            print("✅ Tables and indexes created/verified")
    
    # ==================== User Operations ====================
    
    async def create_or_update_user(
        self, 
        email: str, 
        name: Optional[str] = None, 
        picture_url: Optional[str] = None
    ) -> Optional[int]:
        """Create or update user and return user_id"""
        if not self.pool:
            # Use in-memory storage
            if email not in self.memory_users:
                self.memory_users[email] = {
                    'id': self.memory_user_id_counter,
                    'email': email,
                    'name': name,
                    'picture_url': picture_url
                }
                user_id = self.memory_user_id_counter
                self.memory_user_id_counter += 1
            else:
                self.memory_users[email]['name'] = name
                self.memory_users[email]['picture_url'] = picture_url
                user_id = self.memory_users[email]['id']
            
            print(f"✅ In-memory user created/updated: {email} (ID: {user_id})")
            return user_id
        
        try:
            async with self.pool.acquire() as conn:
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
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        if not self.pool:
            for user in self.memory_users.values():
                if user['id'] == user_id:
                    return User(
                        id=user['id'],
                        email=user['email'],
                        name=user.get('name'),
                        picture=user.get('picture_url')
                    )
            return None
        
        if not user_id:
            return None
        
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    'SELECT id, email, name, picture_url FROM users WHERE id = $1',
                    user_id
                )
                if row:
                    return User(
                        id=row['id'],
                        email=row['email'],
                        name=row['name'],
                        picture=row['picture_url']
                    )
        except Exception as e:
            print(f"⚠️  Error getting user: {e}")
        
        return None
    
    # ==================== Profile Operations ====================
    
    async def load_profile(self, user_id: Optional[int] = None) -> UserProfile:
        """Load user profile from database"""
        default_folders = [{"name": "Likes", "id": "likes", "papers": []}]
        
        if not self.pool:
            if user_id and user_id in self.memory_profiles:
                profile = self.memory_profiles[user_id]
                return UserProfile(
                    topics=profile.get('topics', []),
                    authors=profile.get('authors', []),
                    folders=profile.get('folders', default_folders)
                )
            return UserProfile(topics=[], authors=[], folders=default_folders)
        
        try:
            async with self.pool.acquire() as conn:
                if user_id:
                    row = await conn.fetchrow(
                        'SELECT topics, authors, folders FROM profiles WHERE user_id = $1 ORDER BY updated_at DESC LIMIT 1',
                        user_id
                    )
                else:
                    row = await conn.fetchrow(
                        'SELECT topics, authors, folders FROM profiles ORDER BY updated_at DESC LIMIT 1'
                    )
                
                if row:
                    folders = json.loads(row['folders']) if row['folders'] else default_folders
                    # Ensure default Likes folder exists
                    if not any(f['id'] == 'likes' for f in folders):
                        folders.insert(0, {"name": "Likes", "id": "likes", "papers": []})
                    
                    return UserProfile(
                        topics=json.loads(row['topics']) if row['topics'] else [],
                        authors=json.loads(row['authors']) if row['authors'] else [],
                        folders=folders
                    )
        except Exception as e:
            print(f"⚠️  Error loading profile: {e}")
            import traceback
            traceback.print_exc()
        
        return UserProfile(topics=[], authors=[], folders=default_folders)
    
    async def save_profile(
        self, 
        topics_list: List[str], 
        authors_list: List[str], 
        user_id: Optional[int] = None
    ):
        """Save user profile (topics and authors)"""
        if not self.pool:
            if user_id:
                if user_id not in self.memory_profiles:
                    self.memory_profiles[user_id] = {
                        "topics": [],
                        "authors": [],
                        "folders": [{"name": "Likes", "id": "likes", "papers": []}]
                    }
                self.memory_profiles[user_id]["topics"] = topics_list
                self.memory_profiles[user_id]["authors"] = authors_list
                print(f"✅ Profile saved to in-memory storage for user {user_id}")
            return
        
        try:
            async with self.pool.acquire() as conn:
                # Check if profile exists to preserve folders
                existing = await conn.fetchrow(
                    'SELECT folders FROM profiles WHERE user_id = $1 ORDER BY updated_at DESC LIMIT 1',
                    user_id
                )
                
                if existing:
                    folders = existing['folders'] if existing['folders'] else json.dumps([{"name": "Likes", "id": "likes", "papers": []}])
                    await conn.execute('''
                        UPDATE profiles 
                        SET topics = $1, authors = $2, folders = $3, updated_at = NOW()
                        WHERE user_id = $4
                    ''', json.dumps(topics_list), json.dumps(authors_list), folders, user_id)
                    print(f"✅ Profile updated in database for user {user_id}")
                else:
                    await conn.execute('''
                        INSERT INTO profiles (user_id, topics, authors, folders)
                        VALUES ($1, $2, $3, $4)
                    ''', user_id, json.dumps(topics_list), json.dumps(authors_list), 
                       json.dumps([{"name": "Likes", "id": "likes", "papers": []}]))
                    print(f"✅ New profile created in database for user {user_id}")
        except Exception as e:
            print(f"⚠️  Error saving profile: {e}")
            import traceback
            traceback.print_exc()
    
    async def save_folders(self, folders_list: List[Dict], user_id: Optional[int] = None):
        """Save user folders to database"""
        if not self.pool:
            if user_id:
                if user_id not in self.memory_profiles:
                    self.memory_profiles[user_id] = {"topics": [], "authors": [], "folders": []}
                self.memory_profiles[user_id]["folders"] = folders_list
                print(f"✅ Folders saved to in-memory storage for user {user_id}")
            return
        
        try:
            async with self.pool.acquire() as conn:
                # Check if profile exists
                profile = await conn.fetchrow(
                    'SELECT id FROM profiles WHERE user_id = $1 ORDER BY updated_at DESC LIMIT 1',
                    user_id
                )
                
                if profile:
                    await conn.execute('''
                        UPDATE profiles 
                        SET folders = $1, updated_at = NOW()
                        WHERE user_id = $2
                    ''', json.dumps(folders_list), user_id)
                    print(f"✅ Folders updated in database for user {user_id}")
                else:
                    await conn.execute('''
                        INSERT INTO profiles (user_id, topics, authors, folders)
                        VALUES ($1, $2, $3, $4)
                    ''', user_id, json.dumps([]), json.dumps([]), json.dumps(folders_list))
                    print(f"✅ New profile created with folders for user {user_id}")
        except Exception as e:
            print(f"⚠️  Error saving folders: {e}")
            import traceback
            traceback.print_exc()
    
    # ==================== Feedback Operations ====================
    
    async def load_feedback(self, user_id: Optional[int] = None) -> FeedbackResponse:
        """Load user feedback from database"""
        if not self.pool:
            if user_id and user_id in self.memory_feedback:
                user_feedback = self.memory_feedback[user_id]
                liked = [pid for pid, action in user_feedback.items() if action == 'liked']
                disliked = [pid for pid, action in user_feedback.items() if action == 'disliked']
                return FeedbackResponse(liked=liked, disliked=disliked)
            return FeedbackResponse(liked=[], disliked=[])
        
        try:
            async with self.pool.acquire() as conn:
                if user_id:
                    rows = await conn.fetch(
                        'SELECT paper_id, action FROM feedback WHERE user_id = $1',
                        user_id
                    )
                else:
                    rows = await conn.fetch('SELECT paper_id, action FROM feedback')
                
                liked = [row['paper_id'] for row in rows if row['action'] == 'liked']
                disliked = [row['paper_id'] for row in rows if row['action'] == 'disliked']
                return FeedbackResponse(liked=liked, disliked=disliked)
        except Exception as e:
            print(f"⚠️  Error loading feedback: {e}")
        
        return FeedbackResponse(liked=[], disliked=[])
    
    async def save_feedback(self, paper_id: str, action: str, user_id: Optional[int] = None):
        """Save feedback for a paper"""
        if not self.pool:
            if user_id:
                if user_id not in self.memory_feedback:
                    self.memory_feedback[user_id] = {}
                self.memory_feedback[user_id][paper_id] = action
                print(f"✅ Feedback saved to memory: user {user_id}, paper {paper_id}")
            return
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO feedback (user_id, paper_id, action)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (user_id, paper_id) DO UPDATE SET action = $3
                ''', user_id, paper_id, action)
        except Exception as e:
            print(f"⚠️  Error saving feedback: {e}")
    
    async def delete_feedback(self, paper_id: str, user_id: Optional[int] = None):
        """Delete feedback for a paper"""
        if not self.pool:
            if user_id and user_id in self.memory_feedback and paper_id in self.memory_feedback[user_id]:
                del self.memory_feedback[user_id][paper_id]
            return
        
        try:
            async with self.pool.acquire() as conn:
                if user_id:
                    await conn.execute(
                        'DELETE FROM feedback WHERE paper_id = $1 AND user_id = $2',
                        paper_id, user_id
                    )
                else:
                    await conn.execute('DELETE FROM feedback WHERE paper_id = $1', paper_id)
        except Exception as e:
            print(f"⚠️  Error deleting feedback: {e}")
    
    async def clear_all_feedback(self, action: Optional[str] = None, user_id: Optional[int] = None):
        """Clear all feedback or specific action"""
        if not self.pool:
            if user_id and user_id in self.memory_feedback:
                if action:
                    self.memory_feedback[user_id] = {
                        pid: act for pid, act in self.memory_feedback[user_id].items() 
                        if act != action
                    }
                else:
                    self.memory_feedback[user_id] = {}
            return
        
        try:
            async with self.pool.acquire() as conn:
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
        except Exception as e:
            print(f"⚠️  Error clearing feedback: {e}")
    
    # ==================== Paper Operations ====================
    
    async def cache_papers(self, papers: List[Paper]):
        """Cache multiple papers to database"""
        for paper in papers:
            await self.save_paper(paper)
    
    async def save_paper(self, paper: Paper):
        """Save paper metadata to database"""
        if not paper.paper_id:
            return
        
        if not self.pool:
            # Use in-memory storage
            self.memory_papers[paper.paper_id] = paper.model_dump()
            return
        
        try:
            async with self.pool.acquire() as conn:
                await conn.execute('''
                    INSERT INTO papers (paper_id, title, authors, abstract, year, venue, citation_count, url, source, tldr, doi)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
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
                        doi = EXCLUDED.doi,
                        updated_at = NOW()
                ''', 
                    paper.paper_id,
                    paper.title,
                    json.dumps([a.model_dump() for a in paper.authors]),
                    paper.abstract,
                    paper.year,
                    paper.venue,
                    paper.citation_count,
                    paper.url,
                    paper.source,
                    paper.tldr,
                    paper.doi
                )
        except Exception as e:
            print(f"⚠️  Error saving paper: {e}")
    
    async def get_paper(self, paper_id: str) -> Optional[Paper]:
        """Get paper metadata from database"""
        if not self.pool:
            paper_dict = self.memory_papers.get(paper_id)
            return Paper(**paper_dict) if paper_dict else None
        
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    'SELECT * FROM papers WHERE paper_id = $1',
                    paper_id
                )
                if row:
                    return self._row_to_paper(row)
        except Exception as e:
            print(f"⚠️  Error getting paper: {e}")
        
        return None
    
    async def get_papers_by_ids(self, paper_ids: List[str]) -> List[Paper]:
        """Get multiple papers by their IDs"""
        if not self.pool:
            papers = []
            for pid in paper_ids:
                paper_dict = self.memory_papers.get(pid)
                if paper_dict:
                    papers.append(Paper(**paper_dict))
            return papers
        
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(
                    'SELECT * FROM papers WHERE paper_id = ANY($1) ORDER BY created_at DESC',
                    paper_ids
                )
                return [self._row_to_paper(row) for row in rows]
        except Exception as e:
            print(f"⚠️  Error getting papers: {e}")
        
        return []
    
    def _row_to_paper(self, row) -> Paper:
        """Convert database row to Paper model"""
        from ..models.paper import Author
        
        authors_data = json.loads(row['authors']) if isinstance(row['authors'], str) else row['authors']
        authors = [Author(**a) if isinstance(a, dict) else a for a in authors_data]
        
        return Paper(
            paperId=row['paper_id'],
            title=row['title'],
            abstract=row['abstract'],
            authors=authors,
            year=row['year'],
            venue=row['venue'],
            citationCount=row['citation_count'],
            url=row['url'],
            tldr=row['tldr'],
            source=row['source'],
            doi=row.get('doi')
        )
