# Database Setup for Research Doomscroll

## ✅ STATUS: Database Integration Complete!

The application has been updated to use PostgreSQL for persistent storage.

### What Changed:
- ✅ Created `database.py` module with asyncpg for PostgreSQL
- ✅ All file-based storage replaced with database calls
- ✅ Async database operations throughout the app
- ✅ Startup event initializes database connection pool
- ✅ Automatic fallback to in-memory storage if no DATABASE_URL

### Database Tables:
1. **profiles** - User interests (topics & authors)
2. **feedback** - Liked/disliked papers
3. **paper_cache** - Cached search results (future)

---

## 🚀 Deployment Instructions for Render

### Step 1: Create PostgreSQL Database on Render

1. Go to your Render dashboard: https://dashboard.render.com
2. Click "New +" → "PostgreSQL"
3. Configure:
   - **Name**: `research-doomscroll-db`
   - **Database**: `research_doomscroll`
   - **User**: (auto-generated)
   - **Region**: Same as your web service (for lower latency)
   - **Plan**: Free (1GB storage, no backups)
4. Click "Create Database"
5. Wait for database to be created (usually 1-2 minutes)

### Step 2: Get Database Connection URL

1. Click on your new database in the dashboard
2. Scroll to "Connections" section
3. Copy the **Internal Database URL** (starts with `postgres://`)
   - Internal URL is faster and doesn't count against bandwidth limits
   - Format: `postgres://user:password@hostname/database`

### Step 3: Add DATABASE_URL to Your Web Service

1. Go to your web service: `research-doomscroll`
2. Click "Environment" in the left sidebar
3. Click "Add Environment Variable"
4. Add:
   - **Key**: `DATABASE_URL`
   - **Value**: Paste the Internal Database URL you copied
5. Click "Save Changes"

### Step 4: Deploy!

Your web service will automatically redeploy with the new environment variable. The database will be initialized on first startup.

**That's it!** Your app now has persistent storage that survives restarts. 🎉

---

## 📊 What Gets Stored in the Database

### User Profile
- Search topics (comma-separated)
- Favorite authors (comma-separated)
- Persists across sessions

### Feedback
- Liked papers (paper IDs)
- Disliked papers (paper IDs)
- Used for recommendations

### Benefits:
- ✅ Data persists across deployments
- ✅ No more losing preferences on restart
- ✅ Better recommendation quality over time
- ✅ Faster queries with indexed lookups
- ✅ All on free tier! (1GB storage included)

---

## 🔧 Troubleshooting

### Database connection fails?
- Check that DATABASE_URL is set correctly in environment variables
- Ensure database and web service are in the same region
- App will fall back to in-memory storage if DATABASE_URL is not set
- Check logs for connection errors

### Need to reset database?
Run these SQL commands in the Render database shell:
```sql
DROP TABLE IF EXISTS profiles;
DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS paper_cache;
```
Then restart your web service to recreate tables.

### Want to check what's in your database?
Use Render's built-in database shell:
1. Go to your database in Render dashboard
2. Click "Shell" tab
3. Run SQL queries like:
```sql
-- Check profiles
SELECT * FROM profiles;

-- Check feedback
SELECT * FROM feedback ORDER BY created_at DESC;

-- Count liked/disliked papers
SELECT 
  SUM(CASE WHEN liked THEN 1 ELSE 0 END) as total_liked,
  SUM(CASE WHEN NOT liked THEN 1 ELSE 0 END) as total_disliked
FROM feedback;
```

### Database connection string format
The DATABASE_URL should look like:
```
postgres://user:password@hostname/database
```

If you copied the External URL by mistake, you can use it but it's slower and counts against bandwidth. Get the Internal URL instead from the Connections section.

---

## 🎯 Next Steps

1. Deploy this update to Render (git push)
2. Add DATABASE_URL environment variable
3. Your data will now persist!
4. Consider implementing paper_cache table for better performance
