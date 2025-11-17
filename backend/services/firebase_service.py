"""
Firebase Firestore Service

Handles all Firebase Firestore operations for users, profiles, feedback, folders, and papers.
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
from firebase_admin import credentials, initialize_app, firestore
import firebase_admin

from ..config import get_settings
from ..models.paper import Paper
from ..models.user import User, UserProfile
from ..models.folder import Folder
from ..models.feedback import FeedbackResponse


class FirebaseService:
    """Service for Firebase Firestore operations"""
    
    def __init__(self):
        self.settings = get_settings()
        self.db: Optional[firestore.Client] = None
        self._initialized = False
    
    async def init_firebase(self):
        """Initialize Firebase Admin SDK and Firestore client"""
        if not self.settings.use_firebase:
            print("⚠️  Firebase is disabled in settings")
            self._initialized = False
            return
        
        if not self.settings.firebase_project_id:
            print("⚠️  FIREBASE_PROJECT_ID not set, skipping Firebase initialization")
            return
        
        if self._initialized:
            return
        
        try:
            # Initialize Firebase Admin SDK
            # Clear any existing apps if project ID changed
            if firebase_admin._apps:
                for app in firebase_admin._apps:
                    try:
                        firebase_admin.delete_app(app)
                    except:
                        pass
            
            if not firebase_admin._apps:
                if self.settings.firebase_credentials_path:
                    # Use service account credentials file
                    import os
                    from pathlib import Path
                    
                    # Resolve credentials path
                    cred_path = os.path.abspath(self.settings.firebase_credentials_path)
                    if not os.path.exists(cred_path):
                        # Try relative to project root
                        project_root = Path(__file__).parent.parent.parent
                        cred_path = project_root / self.settings.firebase_credentials_path
                    
                    if not os.path.exists(cred_path):
                        raise FileNotFoundError(f"Firebase credentials file not found: {self.settings.firebase_credentials_path}")
                    
                    # Load credentials
                    cred = credentials.Certificate(str(cred_path))
                    
                    # Use project ID from .env (user preference)
                    # The service account credentials will be validated against this project
                    project_id = self.settings.firebase_project_id
                    if not project_id:
                        # Fallback to credentials file project ID if .env doesn't have it
                        import json
                        with open(cred_path, 'r') as f:
                            cred_data = json.load(f)
                            project_id = cred_data.get('project_id')
                    
                    initialize_app(cred, {
                        'projectId': project_id,
                    })
                    print(f"✅ Firebase Admin SDK initialized with project: {project_id}")
                else:
                    # Use default credentials (for Cloud Run, GCP, etc.)
                    initialize_app()
                    print("✅ Firebase Admin SDK initialized with default credentials")
            
            # Get Firestore client
            self.db = firestore.client()
            self._initialized = True
            print("✅ Firebase Firestore initialized successfully")
            
        except Exception as e:
            print(f"❌ Firebase initialization failed: {e}")
            import traceback
            traceback.print_exc()
            self.db = None
    
    def _get_timestamp(self):
        """Get current Firestore timestamp"""
        return firestore.SERVER_TIMESTAMP
    
    # ==================== User Operations ====================
    
    async def create_or_update_user(
        self,
        google_uid: str,
        email: str,
        name: Optional[str] = None,
        picture_url: Optional[str] = None
    ) -> Optional[str]:
        """Create or update user profile in Firestore"""
        if not self.db:
            return None
        
        try:
            user_ref = self.db.collection('users').document(google_uid).collection('profile').document('data')
            
            # Get existing user to preserve data
            existing = user_ref.get()
            existing_data = existing.to_dict() if existing.exists else {}
            
            user_data = {
                'uid': google_uid,
                'email': email,
                'name': name,
                'pictureUrl': picture_url,
                'lastLoginAt': self._get_timestamp(),
                'updatedAt': self._get_timestamp(),
            }
            
            # Preserve existing data if updating
            if existing.exists:
                user_data['topics'] = existing_data.get('topics', [])
                user_data['authors'] = existing_data.get('authors', [])
                user_data['createdAt'] = existing_data.get('createdAt', self._get_timestamp())
                user_data['totalLikes'] = existing_data.get('totalLikes', 0)
                user_data['totalFolders'] = existing_data.get('totalFolders', 0)
                user_data['totalFollowers'] = existing_data.get('totalFollowers', 0)
                user_data['totalFollowing'] = existing_data.get('totalFollowing', 0)
                user_data['publicProfile'] = existing_data.get('publicProfile', False)
                user_data['emailNotifications'] = existing_data.get('emailNotifications', True)
            else:
                # New user defaults
                user_data['topics'] = []
                user_data['authors'] = []
                user_data['createdAt'] = self._get_timestamp()
                user_data['totalLikes'] = 0
                user_data['totalFolders'] = 0
                user_data['totalFollowers'] = 0
                user_data['totalFollowing'] = 0
                user_data['publicProfile'] = False
                user_data['emailNotifications'] = True
            
            user_ref.set(user_data, merge=True)
            print(f"✅ User created/updated in Firestore: {email} (UID: {google_uid})")
            return google_uid
            
        except Exception as e:
            print(f"❌ Error creating/updating user in Firestore: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def get_user_by_uid(self, google_uid: str) -> Optional[Dict]:
        """Get user profile by Google UID"""
        if not self.db:
            return None
        
        try:
            user_ref = self.db.collection('users').document(google_uid).collection('profile').document('data')
            doc = user_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
            
        except Exception as e:
            print(f"❌ Error getting user from Firestore: {e}")
            return None
    
    # ==================== Profile Operations ====================
    
    async def load_profile(self, google_uid: str) -> UserProfile:
        """Load user profile from Firestore"""
        if not self.db:
            return UserProfile(topics=[], authors=[], folders=[])
        
        try:
            # Always load folders (this ensures Likes folder exists)
            folders = await self._load_user_folders(google_uid)
            
            # Ensure Likes folder is always first
            likes_folder = next((f for f in folders if f.get('id') == 'likes'), None)
            if likes_folder:
                folders = [likes_folder] + [f for f in folders if f.get('id') != 'likes']
            
            user_ref = self.db.collection('users').document(google_uid).collection('profile').document('data')
            doc = user_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                return UserProfile(
                    topics=data.get('topics', []),
                    authors=data.get('authors', []),
                    folders=folders
                )
            
            # Even if profile doesn't exist, return folders (which includes Likes)
            return UserProfile(topics=[], authors=[], folders=folders)
            
        except Exception as e:
            print(f"❌ Error loading profile from Firestore: {e}")
            import traceback
            traceback.print_exc()
            return UserProfile(topics=[], authors=[], folders=[])
    
    async def save_profile(
        self,
        google_uid: str,
        topics_list: List[str],
        authors_list: List[str]
    ) -> bool:
        """Save user profile (topics and authors) to Firestore"""
        if not self.db:
            return False
        
        try:
            user_ref = self.db.collection('users').document(google_uid).collection('profile').document('data')
            user_ref.set({
                'topics': topics_list,
                'authors': authors_list,
                'updatedAt': self._get_timestamp(),
            }, merge=True)
            
            print(f"✅ Profile saved to Firestore for user {google_uid}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving profile to Firestore: {e}")
            return False
    
    async def _load_user_folders(self, google_uid: str) -> List[Dict]:
        """Load all folders for a user, ensuring Likes folder exists"""
        # Ensure Firebase is initialized
        if not self._initialized:
            await self.init_firebase()
        
        if not self.db:
            print(f"⚠️  Cannot load folders: Firebase DB not initialized for user {google_uid}")
            return []
        
        try:
            # Ensure Likes folder exists
            await self._ensure_likes_folder_exists(google_uid)
            
            folders_ref = self.db.collection('folders').document(google_uid).collection('user_folders')
            docs = folders_ref.stream()
            
            folders = []
            for doc in docs:
                folder_data = doc.to_dict()
                # Get paper IDs and load full paper details
                paper_ids = folder_data.get('paperIds', [])
                papers = []
                if paper_ids:
                    papers = await self.get_papers_by_ids(paper_ids)
                    papers = [p.model_dump(by_alias=True) if hasattr(p, 'model_dump') else p for p in papers]
                
                folders.append({
                    'id': doc.id,
                    'name': folder_data.get('name', ''),
                    'description': folder_data.get('description'),
                    'papers': papers,  # Load full paper details
                    'created_at': folder_data.get('createdAt'),
                })
            
            # Ensure Likes folder is in the list and load its papers
            likes_exists = any(f.get('id') == 'likes' for f in folders)
            if not likes_exists:
                print(f"⚠️  Likes folder not found in folders list, creating it...")
                # Load papers for Likes folder from feedback
                likes_paper_ids = []
                try:
                    feedback_ref = self.db.collection('feedback').document(google_uid).collection('papers')
                    feedback_docs = feedback_ref.stream()
                    for feedback_doc in feedback_docs:
                        feedback_data = feedback_doc.to_dict()
                        if feedback_data.get('action') == 'liked':
                            likes_paper_ids.append(feedback_doc.id)
                    
                    # Load full paper details for liked papers
                    likes_papers = []
                    if likes_paper_ids:
                        likes_papers = await self.get_papers_by_ids(likes_paper_ids)
                        likes_papers = [p.model_dump(by_alias=True) if hasattr(p, 'model_dump') else p for p in likes_papers]
                except Exception as e:
                    print(f"⚠️  Error loading papers for Likes folder: {e}")
                    likes_papers = []
                
                folders.insert(0, {
                    'id': 'likes',
                    'name': 'Likes',
                    'description': 'Papers you have liked',
                    'papers': likes_papers,
                    'created_at': None,
                })
            else:
                # Load papers for existing Likes folder
                likes_folder = next((f for f in folders if f.get('id') == 'likes'), None)
                if likes_folder:
                    try:
                        # Get paper IDs from feedback collection
                        feedback_ref = self.db.collection('feedback').document(google_uid).collection('papers')
                        feedback_docs = feedback_ref.stream()
                        likes_paper_ids = []
                        for feedback_doc in feedback_docs:
                            feedback_data = feedback_doc.to_dict()
                            if feedback_data.get('action') == 'liked':
                                likes_paper_ids.append(feedback_doc.id)
                        
                        # Load full paper details
                        if likes_paper_ids:
                            likes_papers = await self.get_papers_by_ids(likes_paper_ids)
                            likes_papers = [p.model_dump(by_alias=True) if hasattr(p, 'model_dump') else p for p in likes_papers]
                            likes_folder['papers'] = likes_papers
                    except Exception as e:
                        print(f"⚠️  Error loading papers for Likes folder: {e}")
            
            print(f"✅ Loaded {len(folders)} folders for user {google_uid}")
            return folders
            
        except Exception as e:
            print(f"❌ Error loading folders from Firestore for user {google_uid}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    # ==================== Feedback Operations ====================
    
    async def load_feedback(self, google_uid: str) -> FeedbackResponse:
        """Load user feedback (likes/dislikes) from Firestore"""
        # Ensure Firebase is initialized
        if not self._initialized:
            await self.init_firebase()
        
        if not self.db:
            print(f"⚠️  Firebase DB not available for loading feedback")
            return FeedbackResponse(liked=[], disliked=[])
        
        try:
            feedback_ref = self.db.collection('feedback').document(google_uid).collection('papers')
            
            # Get all feedback documents
            docs = feedback_ref.stream()
            
            liked = []
            disliked = []
            
            for doc in docs:
                data = doc.to_dict()
                action = data.get('action', '')
                paper_id = doc.id
                
                if action == 'liked':
                    liked.append(paper_id)
                elif action == 'disliked':
                    disliked.append(paper_id)
            
            return FeedbackResponse(liked=liked, disliked=disliked)
            
        except Exception as e:
            print(f"❌ Error loading feedback from Firestore: {e}")
            return FeedbackResponse(liked=[], disliked=[])
    
    async def save_feedback(
        self,
        google_uid: str,
        paper_id: str,
        action: str,  # 'liked' or 'disliked'
        paper_data: Optional[Paper] = None
    ) -> bool:
        """Save feedback for a paper and add to Likes folder if liked - optimized with batch writes"""
        if not self.db:
            print(f"⚠️  Cannot save feedback: Firebase DB not initialized")
            return False
        
        try:
            # Ensure Firebase is initialized
            if not self._initialized:
                await self.init_firebase()
            
            if not self.db:
                print(f"❌ Firebase DB not available for saving feedback")
                return False
            
            # Use batch write for multiple operations
            batch = self.db.batch()
            
            # 1. Save feedback
            feedback_ref = self.db.collection('feedback').document(google_uid).collection('papers').document(paper_id)
            batch.set(feedback_ref, {
                'userId': google_uid,
                'paperId': paper_id,
                'action': action,
                'createdAt': self._get_timestamp(),
                'updatedAt': self._get_timestamp(),
            }, merge=True)
            
            # If liked, add to Likes folder and cache paper in batch
            if action == 'liked':
                print(f"❤️  Adding paper {paper_id} to Likes folder for user {google_uid}")
                
                # 2. Ensure Likes folder exists (check and create if needed)
                likes_folder_ref = self.db.collection('folders').document(google_uid).collection('user_folders').document('likes')
                likes_doc = likes_folder_ref.get()
                
                if not likes_doc.exists:
                    batch.set(likes_folder_ref, {
                        'userId': google_uid,
                        'folderId': 'likes',
                        'name': 'Likes',
                        'description': 'Papers you have liked',
                        'paperIds': [paper_id],
                        'createdAt': self._get_timestamp(),
                        'updatedAt': self._get_timestamp(),
                        'paperCount': 1,
                        'isPublic': False,
                    })
                else:
                    # 3. Add paper to Likes folder using ArrayUnion
                    data = likes_doc.to_dict()
                    paper_ids = data.get('paperIds', [])
                    if paper_id not in paper_ids:
                        batch.update(likes_folder_ref, {
                            'paperIds': firestore.ArrayUnion([paper_id]),
                            'paperCount': len(paper_ids) + 1,
                            'updatedAt': self._get_timestamp(),
                        })
                
                # 4. Cache paper if provided
                if paper_data:
                    paper_ref = self.db.collection('papers').document(paper_id)
                    authors_data = [a.model_dump(by_alias=True) if hasattr(a, 'model_dump') else a for a in paper_data.authors]
                    batch.set(paper_ref, {
                        'paperId': paper_data.paper_id,
                        'title': paper_data.title,
                        'authors': authors_data,
                        'abstract': paper_data.abstract,
                        'tldr': paper_data.tldr,
                        'year': paper_data.year,
                        'venue': paper_data.venue,
                        'doi': paper_data.doi,
                        'url': paper_data.url,
                        'citationCount': paper_data.citation_count,
                        'source': paper_data.source or 'openalex',
                        'cachedAt': self._get_timestamp(),
                        'updatedAt': self._get_timestamp(),
                    }, merge=True)
                    print(f"💾 Caching paper {paper_id} for user {google_uid}")
            
            # Commit all operations in a single batch
            batch.commit()
            
            print(f"✅ Feedback saved to Firestore: user {google_uid}, paper {paper_id}, action {action}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving feedback to Firestore: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def _ensure_likes_folder_exists(self, google_uid: str):
        """Ensure the 'Likes' folder exists for a user"""
        # Ensure Firebase is initialized
        if not self._initialized:
            await self.init_firebase()
        
        if not self.db:
            print(f"⚠️  Cannot ensure Likes folder exists: Firebase DB not initialized for user {google_uid}")
            return
        
        try:
            likes_folder_ref = self.db.collection('folders').document(google_uid).collection('user_folders').document('likes')
            doc = likes_folder_ref.get()
            
            if not doc.exists:
                print(f"📁 Creating 'Likes' folder for user {google_uid}")
                likes_folder_ref.set({
                    'userId': google_uid,
                    'folderId': 'likes',
                    'name': 'Likes',
                    'description': 'Papers you have liked',
                    'paperIds': [],
                    'createdAt': self._get_timestamp(),
                    'updatedAt': self._get_timestamp(),
                    'paperCount': 0,
                    'isPublic': False,
                })
                print(f"✅ Created 'Likes' folder for user {google_uid}")
            else:
                print(f"✅ 'Likes' folder already exists for user {google_uid}")
        except Exception as e:
            print(f"❌ Error ensuring Likes folder exists for user {google_uid}: {e}")
            import traceback
            traceback.print_exc()
    
    async def delete_feedback(
        self,
        google_uid: str,
        paper_id: str
    ) -> bool:
        """Delete feedback for a paper and remove from Likes folder if it was liked"""
        if not self.db:
            return False
        
        try:
            # Check if it was liked before deleting
            feedback_ref = self.db.collection('feedback').document(google_uid).collection('papers').document(paper_id)
            doc = feedback_ref.get()
            was_liked = False
            if doc.exists:
                data = doc.to_dict()
                was_liked = data.get('action') == 'liked'
            
            # Delete feedback
            feedback_ref.delete()
            
            # If it was liked, remove from Likes folder
            if was_liked:
                await self.remove_paper_from_folder(google_uid, 'likes', paper_id)
            
            print(f"✅ Feedback deleted from Firestore: user {google_uid}, paper {paper_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting feedback from Firestore: {e}")
            return False
    
    async def _increment_user_stat(self, google_uid: str, stat_name: Optional[str] = None):
        """Increment user statistics"""
        if not self.db or not stat_name:
            return
        
        try:
            user_ref = self.db.collection('users').document(google_uid).collection('profile').document('data')
            user_ref.update({
                stat_name: firestore.Increment(1),
            })
        except Exception as e:
            print(f"⚠️  Error incrementing user stat: {e}")
    
    # ==================== Folder Operations ====================
    
    async def create_folder(
        self,
        google_uid: str,
        folder_id: str,
        name: str,
        description: Optional[str] = None
    ) -> bool:
        """Create a new folder"""
        if not self.db:
            return False
        
        try:
            folder_ref = self.db.collection('folders').document(google_uid).collection('user_folders').document(folder_id)
            folder_ref.set({
                'userId': google_uid,
                'folderId': folder_id,
                'name': name,
                'description': description,
                'paperIds': [],
                'createdAt': self._get_timestamp(),
                'updatedAt': self._get_timestamp(),
                'paperCount': 0,
                'isPublic': False,
            })
            
            # Update user stats
            await self._increment_user_stat(google_uid, 'totalFolders')
            
            print(f"✅ Folder created in Firestore: {name} (ID: {folder_id})")
            return True
            
        except Exception as e:
            print(f"❌ Error creating folder in Firestore: {e}")
            return False
    
    async def get_folder(self, google_uid: str, folder_id: str) -> Optional[Dict]:
        """Get a folder by ID with full paper details"""
        if not self.db:
            # Return empty Likes folder if DB not initialized
            if folder_id.lower() == 'likes':
                return {
                    'id': 'likes',
                    'name': 'Likes',
                    'description': 'Papers you have liked',
                    'papers': [],
                    'created_at': None,
                }
            return None
        
        try:
            # Always ensure Likes folder exists before getting it
            if folder_id.lower() == 'likes':
                await self._ensure_likes_folder_exists(google_uid)
            
            folder_ref = self.db.collection('folders').document(google_uid).collection('user_folders').document(folder_id)
            doc = folder_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                paper_ids = data.get('paperIds', [])
                
                # Load full paper details
                papers = []
                if paper_ids:
                    papers = await self.get_papers_by_ids(paper_ids)
                    papers = [p.model_dump(by_alias=True) if hasattr(p, 'model_dump') else p for p in papers]
                
                return {
                    'id': doc.id,
                    'name': data.get('name', ''),
                    'description': data.get('description'),
                    'papers': papers,
                    'created_at': data.get('createdAt'),
                }
            
            # If Likes folder doesn't exist, create it and return empty
            if folder_id.lower() == 'likes':
                await self._ensure_likes_folder_exists(google_uid)
                return {
                    'id': 'likes',
                    'name': 'Likes',
                    'description': 'Papers you have liked',
                    'papers': [],
                    'created_at': None,
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting folder from Firestore: {e}")
            import traceback
            traceback.print_exc()
            # Return empty Likes folder on error if that's what was requested
            if folder_id.lower() == 'likes':
                return {
                    'id': 'likes',
                    'name': 'Likes',
                    'description': 'Papers you have liked',
                    'papers': [],
                    'created_at': None,
                }
            return None
    
    async def get_all_folders(self, google_uid: str) -> List[Dict]:
        """Get all folders for a user, ensuring Likes folder exists and is always returned"""
        # Ensure Firebase is initialized
        if not self._initialized:
            await self.init_firebase()
        
        if not self.db:
            # Return empty Likes folder if DB not initialized
            return [{
                'id': 'likes',
                'name': 'Likes',
                'description': 'Papers you have liked',
                'papers': [],
                'created_at': None,
            }]
        
        try:
            # ALWAYS ensure Likes folder exists
            await self._ensure_likes_folder_exists(google_uid)
            
            folders_ref = self.db.collection('folders').document(google_uid).collection('user_folders')
            docs = folders_ref.stream()
            
            folders = []
            for doc in docs:
                data = doc.to_dict()
                paper_ids = data.get('paperIds', [])
                # Load paper details if needed
                papers = []
                if paper_ids:
                    papers = await self.get_papers_by_ids(paper_ids)
                    papers = [p.model_dump(by_alias=True) if hasattr(p, 'model_dump') else p for p in papers]
                
                folders.append({
                    'id': doc.id,
                    'name': data.get('name', ''),
                    'description': data.get('description'),
                    'papers': papers,
                    'created_at': data.get('createdAt'),
                })
            
            # Ensure Likes folder is always in the list
            likes_exists = any(f.get('id') == 'likes' for f in folders)
            if not likes_exists:
                print(f"⚠️  Likes folder missing from query results, adding it...")
                folders.insert(0, {
                    'id': 'likes',
                    'name': 'Likes',
                    'description': 'Papers you have liked',
                    'papers': [],
                    'created_at': None,
                })
            
            # Ensure Likes folder is always first
            likes_folder = next((f for f in folders if f.get('id') == 'likes'), None)
            if likes_folder:
                folders = [likes_folder] + [f for f in folders if f.get('id') != 'likes']
            
            print(f"✅ Returning {len(folders)} folders (Likes folder included) for user {google_uid}")
            return folders
            
        except Exception as e:
            print(f"❌ Error getting folders from Firestore: {e}")
            import traceback
            traceback.print_exc()
            # Return at least the Likes folder even on error
            return [{
                'id': 'likes',
                'name': 'Likes',
                'description': 'Papers you have liked',
                'papers': [],
                'created_at': None,
            }]
    
    async def add_paper_to_folder(
        self,
        google_uid: str,
        folder_id: str,
        paper_id: str
    ) -> bool:
        """Add a paper to a folder (creates folder if it doesn't exist, especially for Likes)"""
        # Ensure Firebase is initialized
        if not self._initialized:
            await self.init_firebase()
        
        if not self.db:
            print(f"⚠️  Cannot add paper to folder: Firebase DB not initialized")
            return False
        
        try:
            # Ensure Likes folder exists if adding to it
            if folder_id.lower() == 'likes':
                await self._ensure_likes_folder_exists(google_uid)
            
            folder_ref = self.db.collection('folders').document(google_uid).collection('user_folders').document(folder_id)
            doc = folder_ref.get()
            
            if not doc.exists:
                # Create folder if it doesn't exist (shouldn't happen for Likes, but handle it)
                if folder_id.lower() == 'likes':
                    await self._ensure_likes_folder_exists(google_uid)
                    doc = folder_ref.get()  # Re-fetch after creation
                else:
                    print(f"⚠️  Folder {folder_id} does not exist for user {google_uid}")
                    return False
            
            # Get current paper IDs to check if already exists
            data = doc.to_dict()
            paper_ids = data.get('paperIds', [])
            
            # Add paper ID if not already present
            if paper_id not in paper_ids:
                folder_ref.update({
                    'paperIds': firestore.ArrayUnion([paper_id]),
                    'paperCount': len(paper_ids) + 1,
                    'updatedAt': self._get_timestamp(),
                })
                print(f"✅ Added paper {paper_id} to folder {folder_id} for user {google_uid} (now has {len(paper_ids) + 1} papers)")
                return True
            else:
                print(f"ℹ️  Paper {paper_id} already in folder {folder_id}")
                return True
                
        except Exception as e:
            print(f"❌ Error adding paper to folder: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def remove_paper_from_folder(
        self,
        google_uid: str,
        folder_id: str,
        paper_id: str
    ) -> bool:
        """Remove a paper from a folder"""
        if not self.db:
            return False
        
        try:
            folder_ref = self.db.collection('folders').document(google_uid).collection('user_folders').document(folder_id)
            folder_ref.update({
                'paperIds': firestore.ArrayRemove([paper_id]),
                'paperCount': firestore.Increment(-1),
                'updatedAt': self._get_timestamp(),
            })
            
            print(f"✅ Paper removed from folder: {paper_id} <- {folder_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error removing paper from folder in Firestore: {e}")
            return False
    
    # ==================== Paper Operations ====================
    
    async def cache_paper(self, paper: Paper) -> bool:
        """Cache paper metadata to Firestore"""
        if not self.db or not paper.paper_id:
            return False
        
        try:
            paper_ref = self.db.collection('papers').document(paper.paper_id)
            
            # Convert authors to dict format
            authors_data = [a.model_dump(by_alias=True) if hasattr(a, 'model_dump') else a for a in paper.authors]
            
            paper_data = {
                'paperId': paper.paper_id,
                'title': paper.title,
                'authors': authors_data,
                'abstract': paper.abstract,
                'tldr': paper.tldr,
                'year': paper.year,
                'venue': paper.venue,
                'doi': paper.doi,
                'url': paper.url,
                'citationCount': paper.citation_count,
                'source': paper.source or 'openalex',
                'cachedAt': self._get_timestamp(),
                'updatedAt': self._get_timestamp(),
                'accessCount': firestore.Increment(1),
                'likeCount': 0,  # Will be updated by Cloud Function
                'saveCount': 0,  # Will be updated by Cloud Function
            }
            
            paper_ref.set(paper_data, merge=True)
            return True
            
        except Exception as e:
            print(f"❌ Error caching paper to Firestore: {e}")
            return False
    
    async def get_paper(self, paper_id: str) -> Optional[Paper]:
        """Get paper metadata from Firestore"""
        if not self.db:
            return None
        
        try:
            paper_ref = self.db.collection('papers').document(paper_id)
            doc = paper_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                return self._dict_to_paper(data)
            return None
            
        except Exception as e:
            print(f"❌ Error getting paper from Firestore: {e}")
            return None
    
    async def get_papers_by_ids(self, paper_ids: List[str]) -> List[Paper]:
        """Get multiple papers by their IDs using batch get"""
        if not self.db:
            return []
        
        if not paper_ids:
            return []
        
        try:
            # Use Firestore batch get for efficiency
            paper_refs = [self.db.collection('papers').document(paper_id) for paper_id in paper_ids]
            docs = self.db.get_all(paper_refs)
            
            papers = []
            for doc in docs:
                if doc.exists:
                    data = doc.to_dict()
                    paper = self._dict_to_paper(data)
                    if paper:
                        papers.append(paper)
            
            return papers
            
        except Exception as e:
            print(f"❌ Error getting papers from Firestore: {e}")
            return []
    
    def _dict_to_paper(self, data: Dict) -> Paper:
        """Convert Firestore document dict to Paper model"""
        from ..models.paper import Author
        
        authors_data = data.get('authors', [])
        authors = []
        for a in authors_data:
            if isinstance(a, dict):
                authors.append(Author(**a))
            else:
                authors.append(a)
        
        return Paper(
            paperId=data.get('paperId', ''),
            title=data.get('title', ''),
            abstract=data.get('abstract'),
            authors=authors,
            year=data.get('year'),
            venue=data.get('venue'),
            citationCount=data.get('citationCount'),
            url=data.get('url'),
            tldr=data.get('tldr'),
            source=data.get('source', 'openalex'),
            doi=data.get('doi'),
        )


# Global Firebase service instance
_firebase_service: Optional[FirebaseService] = None


async def get_firebase_service() -> FirebaseService:
    """Get or create Firebase service instance"""
    global _firebase_service
    
    if _firebase_service is None:
        _firebase_service = FirebaseService()
        await _firebase_service.init_firebase()
    
    return _firebase_service

