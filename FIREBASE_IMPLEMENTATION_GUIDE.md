# Firebase Implementation Guide

## Quick Start

### 1. Firebase Project Setup

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase in project
firebase init firestore
```

### 2. Install Firebase Admin SDK (Backend)

```bash
cd backend
pip install firebase-admin
```

### 3. Environment Variables

Add to `.env`:
```
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CREDENTIALS_PATH=path/to/service-account-key.json
```

### 4. Firebase Service Initialization

Create `backend/services/firebase_service.py`:

```python
import firebase_admin
from firebase_admin import credentials, firestore
from ..config import get_settings

settings = get_settings()

# Initialize Firebase Admin SDK
cred = credentials.Certificate(settings.firebase_credentials_path)
firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()
```

## Key Operations

### User Operations

```python
# Create/Update User
def create_or_update_user(google_uid: str, email: str, name: str, picture: str):
    user_ref = db.collection('users').document(google_uid).collection('profile').document('data')
    user_ref.set({
        'uid': google_uid,
        'email': email,
        'name': name,
        'picture': picture,
        'topics': [],
        'authors': [],
        'createdAt': firestore.SERVER_TIMESTAMP,
        'lastLoginAt': firestore.SERVER_TIMESTAMP,
        'updatedAt': firestore.SERVER_TIMESTAMP,
        'totalLikes': 0,
        'totalFolders': 0,
        'totalFollowers': 0,
        'totalFollowing': 0,
    }, merge=True)

# Get User Profile
def get_user_profile(google_uid: str):
    doc = db.collection('users').document(google_uid).collection('profile').document('data').get()
    return doc.to_dict() if doc.exists else None
```

### Feedback Operations

```python
# Like a Paper
def like_paper(google_uid: str, paper_id: str):
    feedback_ref = db.collection('feedback').document(google_uid).collection('papers').document(paper_id)
    feedback_ref.set({
        'userId': google_uid,
        'paperId': paper_id,
        'action': 'liked',
        'createdAt': firestore.SERVER_TIMESTAMP,
        'updatedAt': firestore.SERVER_TIMESTAMP,
    })

# Get User Likes
def get_user_likes(google_uid: str, limit: int = 100):
    likes_ref = db.collection('feedback').document(google_uid).collection('papers')
    query = likes_ref.where('action', '==', 'liked').order_by('createdAt', direction=firestore.Query.DESCENDING).limit(limit)
    return [doc.to_dict() for doc in query.stream()]
```

### Folder Operations

```python
# Create Folder
def create_folder(google_uid: str, folder_id: str, name: str, description: str = None):
    folder_ref = db.collection('folders').document(google_uid).document(folder_id)
    folder_ref.set({
        'userId': google_uid,
        'folderId': folder_id,
        'name': name,
        'description': description,
        'paperIds': [],
        'createdAt': firestore.SERVER_TIMESTAMP,
        'updatedAt': firestore.SERVER_TIMESTAMP,
        'paperCount': 0,
        'isPublic': False,
    })

# Add Paper to Folder
def add_paper_to_folder(google_uid: str, folder_id: str, paper_id: str):
    folder_ref = db.collection('folders').document(google_uid).document(folder_id)
    folder_ref.update({
        'paperIds': firestore.ArrayUnion([paper_id]),
        'paperCount': firestore.Increment(1),
        'updatedAt': firestore.SERVER_TIMESTAMP,
    })
```

## Security Rules File

Save as `firestore.rules`:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    function isAuthenticated() {
      return request.auth != null;
    }
    
    function isOwner(userId) {
      return isAuthenticated() && request.auth.uid == userId;
    }
    
    match /users/{userId} {
      allow read: if isOwner(userId) || resource.data.publicProfile == true;
      allow write: if isOwner(userId);
      
      match /profile {
        allow read: if isOwner(userId) || resource.data.publicProfile == true;
        allow write: if isOwner(userId);
      }
    }
    
    match /feedback/{userId} {
      allow read, write: if isOwner(userId);
      
      match /papers/{paperId} {
        allow read, write: if isOwner(userId);
      }
    }
    
    match /folders/{userId} {
      allow read, write: if isOwner(userId);
      
      match /{folderId} {
        allow read: if isOwner(userId) || resource.data.isPublic == true;
        allow write: if isOwner(userId);
      }
    }
    
    match /papers/{paperId} {
      allow read: if isAuthenticated();
      allow write: if false;
    }
  }
}
```

## Deployment

```bash
# Deploy security rules
firebase deploy --only firestore:rules

# Deploy indexes
firebase deploy --only firestore:indexes
```

