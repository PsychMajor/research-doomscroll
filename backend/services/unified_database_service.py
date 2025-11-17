"""
Unified Database Service

Provides a unified interface that can use either PostgreSQL (via DatabaseService)
or Firebase Firestore (via FirebaseService) based on configuration.
"""

from typing import Optional, List, Dict
from ..config import get_settings
from ..models.paper import Paper
from ..models.user import User, UserProfile
from ..models.folder import Folder
from ..models.feedback import FeedbackResponse
from .database_service import DatabaseService
from .firebase_service import FirebaseService, get_firebase_service


class UnifiedDatabaseService:
    """
    Unified database service that routes to either PostgreSQL or Firebase
    based on configuration.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.use_firebase = self.settings.use_firebase
        
        # Initialize appropriate service
        if self.use_firebase:
            self.firebase_service: Optional[FirebaseService] = None
            self.postgres_service: Optional[DatabaseService] = None
        else:
            self.postgres_service = DatabaseService()
            self.firebase_service = None
    
    async def init(self):
        """Initialize the appropriate database service"""
        if self.use_firebase:
            self.firebase_service = await get_firebase_service()
        else:
            await self.postgres_service.init_db()
    
    # ==================== User Operations ====================
    
    async def create_or_update_user(
        self,
        email: str,
        name: Optional[str] = None,
        picture_url: Optional[str] = None,
        google_uid: Optional[str] = None
    ) -> Optional[str]:
        """
        Create or update user.
        Returns user ID (int for PostgreSQL, Google UID string for Firebase)
        """
        if self.use_firebase and self.firebase_service and google_uid:
            success = await self.firebase_service.create_or_update_user(
                google_uid=google_uid,
                email=email,
                name=name,
                picture_url=picture_url
            )
            return google_uid if success else None
        else:
            # Use PostgreSQL
            if not self.postgres_service:
                self.postgres_service = DatabaseService()
                await self.postgres_service.init_db()
            user_id = await self.postgres_service.create_or_update_user(
                email=email,
                name=name,
                picture_url=picture_url
            )
            return str(user_id) if user_id else None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID (works with both int IDs and Google UIDs)"""
        if self.use_firebase and self.firebase_service:
            user_data = await self.firebase_service.get_user_by_uid(user_id)
            if user_data:
                return User(
                    id=user_data.get('uid', user_id),
                    email=user_data.get('email', ''),
                    name=user_data.get('name'),
                    picture=user_data.get('picture')
                )
            return None
        else:
            # Use PostgreSQL
            if not self.postgres_service:
                self.postgres_service = DatabaseService()
                await self.postgres_service.init_db()
            # Try to convert to int for PostgreSQL
            try:
                int_id = int(user_id)
                return await self.postgres_service.get_user_by_id(int_id)
            except ValueError:
                return None
    
    # ==================== Profile Operations ====================
    
    async def load_profile(self, user_id: str) -> UserProfile:
        """Load user profile"""
        if self.use_firebase and self.firebase_service:
            return await self.firebase_service.load_profile(user_id)
        else:
            # Use PostgreSQL
            if not self.postgres_service:
                self.postgres_service = DatabaseService()
                await self.postgres_service.init_db()
            try:
                int_id = int(user_id)
                return await self.postgres_service.load_profile(user_id=int_id)
            except ValueError:
                return UserProfile(topics=[], authors=[], folders=[])
    
    async def save_profile(
        self,
        user_id: str,
        topics_list: List[str],
        authors_list: List[str]
    ):
        """Save user profile"""
        if self.use_firebase and self.firebase_service:
            await self.firebase_service.save_profile(user_id, topics_list, authors_list)
        else:
            # Use PostgreSQL
            if not self.postgres_service:
                self.postgres_service = DatabaseService()
                await self.postgres_service.init_db()
            try:
                int_id = int(user_id)
                await self.postgres_service.save_profile(topics_list, authors_list, user_id=int_id)
            except ValueError:
                pass
    
    # ==================== Feedback Operations ====================
    
    async def load_feedback(self, user_id: str) -> FeedbackResponse:
        """Load user feedback"""
        if self.use_firebase and self.firebase_service:
            return await self.firebase_service.load_feedback(user_id)
        else:
            # Use PostgreSQL
            if not self.postgres_service:
                self.postgres_service = DatabaseService()
                await self.postgres_service.init_db()
            try:
                int_id = int(user_id)
                return await self.postgres_service.load_feedback(user_id=int_id)
            except ValueError:
                return FeedbackResponse(liked=[], disliked=[])
    
    async def save_feedback(
        self,
        user_id: str,
        paper_id: str,
        action: str,
        paper_data: Optional[Paper] = None
    ):
        """Save feedback"""
        if self.use_firebase and self.firebase_service:
            await self.firebase_service.save_feedback(user_id, paper_id, action, paper_data)
        else:
            # Use PostgreSQL
            if not self.postgres_service:
                self.postgres_service = DatabaseService()
                await self.postgres_service.init_db()
            try:
                int_id = int(user_id)
                await self.postgres_service.save_feedback(paper_id, action, user_id=int_id)
                # For PostgreSQL, also add to Likes folder if liked
                if action == 'liked' and paper_data:
                    await self.postgres_service.save_paper(paper_data)
                    # Add to Likes folder (stored in profile)
                    profile = await self.postgres_service.load_profile(user_id=int_id)
                    folders = profile.folders
                    # Find or create Likes folder
                    likes_folder = next((f for f in folders if f.get('id') == 'likes'), None)
                    if not likes_folder:
                        likes_folder = {'id': 'likes', 'name': 'Likes', 'papers': []}
                        folders.insert(0, likes_folder)
                    # Add paper if not already there
                    if not any(p.get('paperId') == paper_id for p in likes_folder.get('papers', [])):
                        likes_folder['papers'].append(paper_data.model_dump())
                        await self.postgres_service.save_folders(folders, user_id=int_id)
            except ValueError:
                pass
    
    async def delete_feedback(
        self,
        user_id: str,
        paper_id: str
    ):
        """Delete feedback"""
        if self.use_firebase and self.firebase_service:
            await self.firebase_service.delete_feedback(user_id, paper_id)
        else:
            # Use PostgreSQL
            if not self.postgres_service:
                self.postgres_service = DatabaseService()
                await self.postgres_service.init_db()
            try:
                int_id = int(user_id)
                await self.postgres_service.delete_feedback(paper_id, user_id=int_id)
            except ValueError:
                pass
    
    # ==================== Folder Operations ====================
    
    async def create_folder(
        self,
        user_id: str,
        folder_id: str,
        name: str,
        description: Optional[str] = None
    ):
        """Create folder"""
        if self.use_firebase and self.firebase_service:
            await self.firebase_service.create_folder(user_id, folder_id, name, description)
        else:
            # Use PostgreSQL - folders stored in profile
            if not self.postgres_service:
                self.postgres_service = DatabaseService()
                await self.postgres_service.init_db()
            # For PostgreSQL, folders are stored in profiles table as JSONB
            # This would need to be handled differently
            pass
    
    async def get_all_folders(self, user_id: str) -> List[Dict]:
        """Get all folders for user"""
        if self.use_firebase and self.firebase_service:
            folders = await self.firebase_service.get_all_folders(user_id)
            # Ensure Likes folder is always first
            likes_folder = next((f for f in folders if f.get('id') == 'likes'), None)
            if likes_folder:
                folders = [likes_folder] + [f for f in folders if f.get('id') != 'likes']
            return folders
        else:
            # Use PostgreSQL
            if not self.postgres_service:
                self.postgres_service = DatabaseService()
                await self.postgres_service.init_db()
            try:
                int_id = int(user_id)
                profile = await self.postgres_service.load_profile(user_id=int_id)
                folders = profile.folders
                # Ensure Likes folder is always first
                likes_folder = next((f for f in folders if f.get('id') == 'likes'), None)
                if likes_folder:
                    folders = [likes_folder] + [f for f in folders if f.get('id') != 'likes']
                return folders
            except ValueError:
                return []
    
    # ==================== Paper Operations ====================
    
    async def cache_papers(self, papers: List[Paper]):
        """Cache papers"""
        if self.use_firebase and self.firebase_service:
            for paper in papers:
                await self.firebase_service.cache_paper(paper)
        else:
            # Use PostgreSQL
            if not self.postgres_service:
                self.postgres_service = DatabaseService()
                await self.postgres_service.init_db()
            await self.postgres_service.cache_papers(papers)
    
    async def get_papers_by_ids(self, paper_ids: List[str]) -> List[Paper]:
        """Get papers by IDs"""
        if self.use_firebase and self.firebase_service:
            return await self.firebase_service.get_papers_by_ids(paper_ids)
        else:
            # Use PostgreSQL
            if not self.postgres_service:
                self.postgres_service = DatabaseService()
                await self.postgres_service.init_db()
            return await self.postgres_service.get_papers_by_ids(paper_ids)


# Global unified service instance
_unified_db_service: Optional[UnifiedDatabaseService] = None


async def get_unified_db_service() -> UnifiedDatabaseService:
    """Get or create unified database service instance"""
    global _unified_db_service
    
    if _unified_db_service is None:
        _unified_db_service = UnifiedDatabaseService()
        await _unified_db_service.init()
    
    return _unified_db_service

