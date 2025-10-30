# 🎯 Hybrid Setup Guide - Stay on Free Tier!

## Current Status
✅ Backend/API: Deployed on Render.com  
✅ Frontend: Served by FastAPI (Jinja2 templates)  
⚠️ Database: File-based (ephemeral)  

## Free Tier Hybrid Setup

### Option 1: Keep Current Setup (Simplest)
**What you have now works great for free tier!**
- ✅ Everything on Render.com free tier
- ✅ 750 hours/month (enough for personal use)
- ⚠️ App sleeps after 15 min (30s wake-up time)
- ⚠️ Likes/dislikes reset on restart

**Optimization:** Add PostgreSQL for persistence ⬇️

---

### Option 2: Add PostgreSQL (Recommended)
**Keep everything on Render + Add free database**

#### Step 1: Add PostgreSQL on Render
1. Go to [render.com/dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"PostgreSQL"**
3. Settings:
   - **Name**: `research-doomscroll-db`
   - **Database**: `research_doomscroll`
   - **User**: (auto-generated)
   - **Region**: Same as your web service
   - **Instance Type**: **Free**

4. Click **"Create Database"**
5. Copy the **Internal Database URL**

#### Step 2: Connect Web Service to Database
1. Go to your web service: `research-doomscroll`
2. Click **"Environment"** tab
3. Add environment variable:
   - **Key**: `DATABASE_URL`
   - **Value**: (paste Internal Database URL)
4. Click **"Save Changes"**

#### Step 3: Deploy Updated Code
The database module (`database.py`) is already created!

```bash
git add database.py requirements.txt
git commit -m "Add PostgreSQL support for persistent storage"
git push
```

Render will auto-deploy and initialize the database!

#### What You Get:
✅ **Persistent likes/dislikes** (survives restarts)  
✅ **Saved profiles** (your topics/authors saved)  
✅ **Still completely FREE**  
✅ **1GB storage** on free PostgreSQL  

---

### Option 3: Full Hybrid (Advanced)
**Split Frontend & Backend (maximum performance)**

#### Architecture:
```
Frontend (Vercel) → Backend API (Render) → Database (Render PostgreSQL)
```

#### Pros:
- ✅ No sleep time on frontend (Vercel is always fast)
- ✅ Global CDN for frontend
- ✅ Backend can sleep (frontend stays responsive)

#### Cons:
- More complex setup
- Need to rewrite templates to React/Next.js
- More API calls (frontend → backend)

**I can help you migrate to this if you want!**

---

## 📊 Free Tier Limits

### Current Setup (Render Only):
| Service | Free Tier | Your Usage |
|---------|-----------|------------|
| Render Web | 750 hrs/month | ~1 app = 720 hrs |
| Render PostgreSQL | 1GB | Minimal (just user data) |
| **Total Cost** | **$0/month** | ✅ |

### If You Add Vercel:
| Service | Free Tier | Your Usage |
|---------|-----------|------------|
| Vercel Frontend | Unlimited | 0 cost |
| Render Backend | 750 hrs/month | ~360 hrs (sleeps more) |
| Render PostgreSQL | 1GB | Minimal |
| **Total Cost** | **$0/month** | ✅ |

---

## 🚀 Recommended Path

**For your use case, I recommend:**

### Phase 1 (Do Now): Add PostgreSQL
- ✅ Takes 5 minutes
- ✅ Keeps current simple setup
- ✅ Adds persistence
- ✅ Still 100% free

### Phase 2 (Future): Split to Vercel
- Only if you need 24/7 uptime
- Only if wake-up time bothers you
- Requires frontend rewrite (~2-3 hours)

---

## 🎯 Quick Start

**Want to add PostgreSQL right now?**

1. Create database on Render (see Step 1 above)
2. Add `DATABASE_URL` env var
3. Run these commands:
```bash
cd /Users/samayshah/research_doomscroll
git add database.py requirements.txt
git commit -m "Add PostgreSQL for persistent storage"
git push
```

4. Watch Render logs - you'll see:
```
✅ Database initialized successfully
```

**That's it!** Your likes/dislikes now persist forever! 🎉

---

## Need Help?

Let me know which option you want:
1. **Add PostgreSQL** (5 min setup, big improvement)
2. **Full Hybrid Split** (2-3 hours, maximum performance)
3. **Keep as-is** (if you're happy with current setup)
