# Firebase Firestore Database Structure Plan

## Overview
This document outlines a scalable Firebase Firestore database structure for Research Doomscroll that integrates with Google OAuth and supports current features (likes, folders, profiles) plus future features (followers, notifications, recommendations, etc.).

## Design Principles

1. **User-Centric**: All user data is organized under their Google UID
2. **Scalable**: Structure supports millions of users and papers
3. **Real-time Ready**: Collections support real-time listeners
4. **Security First**: Security rules ensure users can only access their own data
5. **Performance Optimized**: Indexed fields and efficient query patterns
6. **Future-Proof**: Structure accommodates planned features

## Database Structure

### Root Collections

```
firestore/
├── users/                    # User profiles and metadata
│   └── {googleUID}/
│       ├── profile           # User profile document
│       ├── preferences       # User preferences document
│       └── stats             # User statistics document
│
├── feedback/                 # User likes/dislikes (subcollection)
│   └── {googleUID}/
│       └── papers/
│           └── {paperId}     # Individual feedback document
│
├── folders/                  # User folders (subcollection)
│   └── {googleUID}/
│       └── {folderId}        # Individual folder document
│
├── papers/                   # Cached paper metadata
│   └── {paperId}             # Paper document (shared across users)
│
├── following/                # User following relationships
│   └── {googleUID}/
│       └── users/
│           └── {followedUID} # Following relationship document
│
├── followers/                # Reverse following (for notifications)
│   └── {googleUID}/
│       └── users/
│           └── {followerUID} # Follower relationship document
│
└── notifications/            # User notifications
    └── {googleUID}/
        └── {notificationId}  # Individual notification document
```

## Detailed Schema

### 1. Users Collection

**Path**: `users/{googleUID}/profile`

```typescript
{
  // User Identity (from Google OAuth)
  uid: string,                    // Google UID (document ID)
  email: string,                  // Google email
  name: string | null,            // Display name
  picture: string | null,         // Profile picture URL
  
  // Profile Data
  topics: string[],               // Research topics/interests
  authors: string[],              // Followed authors
  
  // Metadata
  createdAt: Timestamp,           // Account creation time
  lastLoginAt: Timestamp,         // Last login time
  updatedAt: Timestamp,           // Last profile update
  
  // Settings
  emailNotifications: boolean,    // Email notification preference
  publicProfile: boolean,         // Whether profile is public
  
  // Statistics (denormalized for quick access)
  totalLikes: number,             // Total papers liked
  totalFolders: number,           // Total folders created
  totalFollowers: number,         // Total followers count
  totalFollowing: number,         // Total following count
}
```

**Path**: `users/{googleUID}/preferences`

```typescript
{
  // Display Preferences
  theme: 'light' | 'dark' | 'auto',
  itemsPerPage: number,           // Default: 20
  
  // Notification Preferences
  notifyNewPapers: boolean,       // Notify about new papers in topics
  notifyFollowers: boolean,       // Notify when followed users like papers
  notifyRecommendations: boolean, // Notify about recommendations
  
  // Privacy
  showLikes: boolean,             // Show likes to others
  showFolders: boolean,           // Show folders to others
  
  updatedAt: Timestamp,
}
```

**Path**: `users/{googleUID}/stats`

```typescript
{
  // Activity Stats
  papersViewed: number,
  papersLiked: number,
  papersDisliked: number,
  foldersCreated: number,
  papersSaved: number,
  
  // Engagement Stats
  lastActiveAt: Timestamp,
  streakDays: number,             // Consecutive days active
  
  // Calculated Stats
  averagePapersPerDay: number,
  mostActiveTopic: string | null,
  
  updatedAt: Timestamp,
}
```

### 2. Feedback Collection (Likes/Dislikes)

**Path**: `feedback/{googleUID}/papers/{paperId}`

```typescript
{
  userId: string,                 // Google UID (for queries)
  paperId: string,                // Paper ID (document ID)
  action: 'liked' | 'disliked',   // Feedback type
  createdAt: Timestamp,           // When feedback was given
  updatedAt: Timestamp,           // Last update time
  
  // Optional metadata
  context: {
    source: string,               // Where they saw it (feed, search, etc.)
    topic: string | null,         // Topic context
  },
}
```

**Indexes**:
- `userId` + `createdAt` (descending) - Get user's recent likes
- `paperId` + `action` - Get all likes for a paper
- `userId` + `action` - Get all liked/disliked papers

### 3. Folders Collection

**Path**: `folders/{googleUID}/{folderId}`

```typescript
{
  userId: string,                 // Google UID
  folderId: string,               // Unique folder ID (document ID)
  name: string,                   // Folder name
  description: string | null,     // Optional description
  
  // Papers in folder (references, not full data)
  paperIds: string[],             // Array of paper IDs
  
  // Metadata
  createdAt: Timestamp,
  updatedAt: Timestamp,
  paperCount: number,             // Denormalized count
  
  // Settings
  isPublic: boolean,              // Whether folder is public
  color: string | null,           // Optional folder color
  
  // Statistics
  viewCount: number,              // If public, track views
}
```

**Special Folder**: `likes` folder
- Automatically maintained based on feedback collection
- Not stored separately, generated on-the-fly

### 4. Papers Collection (Shared Cache)

**Path**: `papers/{paperId}`

```typescript
{
  paperId: string,                // OpenAlex ID (document ID)
  
  // Paper Metadata
  title: string,
  authors: Array<{
    name: string,
    id: string | null,
  }>,
  abstract: string | null,
  tldr: string | null,
  
  // Publication Info
  year: number | null,
  venue: string | null,
  doi: string | null,
  url: string | null,
  
  // Metrics
  citationCount: number | null,
  
  // Source
  source: string,                 // 'openalex'
  
  // Caching Metadata
  cachedAt: Timestamp,            // When cached
  updatedAt: Timestamp,           // Last update
  accessCount: number,            // How many times accessed
  
  // Denormalized Stats (updated via Cloud Functions)
  likeCount: number,              // Total likes across all users
  saveCount: number,              // Total saves across all users
}
```

**Indexes**:
- `cachedAt` (descending) - Recent papers
- `likeCount` (descending) - Most liked papers
- `year` (descending) - Recent papers by year

### 5. Following Collection

**Path**: `following/{googleUID}/users/{followedUID}`

```typescript
{
  userId: string,                 // Follower (document parent)
  followedUserId: string,         // User being followed (document ID)
  createdAt: Timestamp,           // When follow relationship started
  
  // Optional metadata
  notificationsEnabled: boolean,  // Get notifications from this user
}
```

**Reverse Collection**: `followers/{googleUID}/users/{followerUID}`
- Mirror of following for efficient queries
- Maintained via Cloud Function

### 6. Notifications Collection

**Path**: `notifications/{googleUID}/{notificationId}`

```typescript
{
  userId: string,                 // Recipient (document parent)
  notificationId: string,         // Unique ID (document ID)
  
  // Notification Type
  type: 'new_paper' | 'follower' | 'like' | 'comment' | 'recommendation',
  
  // Content
  title: string,
  message: string,
  link: string | null,            // Link to relevant content
  
  // Metadata
  read: boolean,                  // Whether notification was read
  createdAt: Timestamp,
  readAt: Timestamp | null,
  
  // Source
  sourceUserId: string | null,    // User who triggered notification
  sourcePaperId: string | null,   // Related paper
}
```

**Indexes**:
- `userId` + `read` + `createdAt` (descending) - Unread notifications
- `userId` + `createdAt` (descending) - All notifications

## Security Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Helper function to check if user is authenticated
    function isAuthenticated() {
      return request.auth != null;
    }
    
    // Helper function to check if user owns the resource
    function isOwner(userId) {
      return isAuthenticated() && request.auth.uid == userId;
    }
    
    // Users collection - users can read/write their own profile
    match /users/{userId} {
      allow read: if isOwner(userId) || resource.data.publicProfile == true;
      allow write: if isOwner(userId);
      
      match /profile {
        allow read: if isOwner(userId) || resource.data.publicProfile == true;
        allow write: if isOwner(userId);
      }
      
      match /preferences {
        allow read, write: if isOwner(userId);
      }
      
      match /stats {
        allow read: if isOwner(userId) || resource.data.publicProfile == true;
        allow write: if false; // Only Cloud Functions can write
      }
    }
    
    // Feedback collection - users can only access their own feedback
    match /feedback/{userId} {
      allow read, write: if isOwner(userId);
      
      match /papers/{paperId} {
        allow read, write: if isOwner(userId);
      }
    }
    
    // Folders collection - users can access their own folders
    match /folders/{userId} {
      allow read, write: if isOwner(userId);
      
      match /{folderId} {
        allow read: if isOwner(userId) || resource.data.isPublic == true;
        allow write: if isOwner(userId);
      }
    }
    
    // Papers collection - read-only for all authenticated users
    match /papers/{paperId} {
      allow read: if isAuthenticated();
      allow write: if false; // Only Cloud Functions can write
    }
    
    // Following collection - users can manage their own following
    match /following/{userId} {
      allow read, write: if isOwner(userId);
      
      match /users/{followedUserId} {
        allow read, write: if isOwner(userId);
      }
    }
    
    // Followers collection - read-only for own followers
    match /followers/{userId} {
      allow read: if isOwner(userId);
      allow write: if false; // Only Cloud Functions can write
      
      match /users/{followerUserId} {
        allow read: if isOwner(userId);
        allow write: if false;
      }
    }
    
    // Notifications collection - users can only access their own
    match /notifications/{userId} {
      allow read, write: if isOwner(userId);
      
      match /{notificationId} {
        allow read, write: if isOwner(userId);
      }
    }
  }
}
```

## Data Access Patterns

### 1. User Login Flow
```
1. User authenticates with Google OAuth
2. Get Google UID from Firebase Auth
3. Check if user document exists: users/{uid}/profile
4. If not exists, create new user document
5. Update lastLoginAt timestamp
6. Load user profile, preferences, stats
```

### 2. Loading User Likes
```
1. Query: feedback/{uid}/papers where action == 'liked'
2. Order by createdAt descending
3. Limit to 100 most recent
4. Use paperIds to fetch full paper data from papers collection
```

### 3. Loading User Folders
```
1. Query: folders/{uid} (get all folders for user)
2. Order by updatedAt descending
3. For each folder, paperIds array contains references
4. Batch fetch papers from papers collection
```

### 4. Following a User
```
1. Create: following/{currentUID}/users/{followedUID}
2. Cloud Function triggers:
   - Create: followers/{followedUID}/users/{currentUID}
   - Increment followers count in users/{followedUID}/stats
   - Increment following count in users/{currentUID}/stats
   - Create notification for followed user
```

### 5. Liking a Paper
```
1. Create/Update: feedback/{uid}/papers/{paperId}
   - Set action: 'liked'
   - Set createdAt, updatedAt
2. Cloud Function triggers:
   - Increment likeCount in papers/{paperId}
   - Increment totalLikes in users/{uid}/stats
   - Create notifications for followers (if enabled)
```

## Cloud Functions (Recommended)

### 1. User Creation Function
- Trigger: New user in Firebase Auth
- Action: Create user profile document with defaults

### 2. Follow Management Function
- Trigger: Document created in `following/{uid}/users/{followedUID}`
- Action: 
  - Create reverse document in `followers/{followedUID}/users/{uid}`
  - Update follower/following counts
  - Create notification

### 3. Feedback Aggregation Function
- Trigger: Document created/updated in `feedback/{uid}/papers/{paperId}`
- Action:
  - Update `papers/{paperId}.likeCount`
  - Update `users/{uid}/stats.totalLikes`
  - Create notifications for followers

### 4. Paper Cache Cleanup Function
- Trigger: Scheduled (daily)
- Action: Remove papers not accessed in 90 days

### 5. Notification Cleanup Function
- Trigger: Scheduled (weekly)
- Action: Delete read notifications older than 30 days

## Migration Strategy

### Phase 1: Setup Firebase
1. Create Firebase project
2. Enable Firestore
3. Set up Firebase Admin SDK in backend
4. Configure security rules

### Phase 2: Dual Write
1. Keep existing PostgreSQL database
2. Write to both PostgreSQL and Firestore
3. Read from PostgreSQL (existing code)
4. Verify data consistency

### Phase 3: Migration
1. Migrate existing user data to Firestore
2. Migrate feedback data
3. Migrate folders data
4. Migrate cached papers

### Phase 4: Switch Over
1. Update backend to read from Firestore
2. Remove PostgreSQL writes
3. Keep PostgreSQL as backup for 30 days
4. Remove PostgreSQL dependency

## Performance Optimizations

1. **Composite Indexes**: Create indexes for common query patterns
2. **Denormalization**: Store counts (likeCount, followerCount) to avoid aggregation queries
3. **Pagination**: Use `limit()` and `startAfter()` for large collections
4. **Caching**: Use Firestore offline persistence for mobile apps
5. **Batch Operations**: Use batch writes for multiple updates
6. **Cloud Functions**: Offload heavy operations to background functions

## Cost Considerations

1. **Reads**: Minimize unnecessary reads (use pagination, cache)
2. **Writes**: Batch writes when possible
3. **Storage**: Clean up old notifications, unused papers
4. **Functions**: Optimize function execution time
5. **Indexes**: Only create necessary indexes

## Future Features Support

### Recommendations
- Store recommendation scores in `users/{uid}/recommendations/{paperId}`
- Update via Cloud Function based on user activity

### Comments/Discussions
- New collection: `comments/{paperId}/{commentId}`
- Link to users via userId field

### Paper Collections
- New collection: `collections/{uid}/{collectionId}`
- Similar to folders but for curated paper lists

### Activity Feed
- New collection: `activity/{uid}/{activityId}`
- Track user activity for feed generation

## Implementation Checklist

- [ ] Set up Firebase project
- [ ] Configure Firestore database
- [ ] Set up Firebase Admin SDK in backend
- [ ] Create security rules
- [ ] Create composite indexes
- [ ] Implement user creation/update functions
- [ ] Implement feedback CRUD operations
- [ ] Implement folder CRUD operations
- [ ] Set up Cloud Functions
- [ ] Create migration scripts
- [ ] Test with sample data
- [ ] Deploy to production
- [ ] Monitor performance and costs

