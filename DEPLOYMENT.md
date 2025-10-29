# 🚀 Deployment Guide for Research Doomscroll

## Quick Deploy Options

### Option 1: Render.com (Recommended - FREE)

1. **Sign up at [render.com](https://render.com)**

2. **Connect GitHub:**
   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select `PsychMajor/research-doomscroll`

3. **Configure:**
   - **Name**: research-doomscroll
   - **Environment**: Python 3
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python -c "import nltk; nltk.download('punkt_tab'); nltk.download('punkt')"
     ```
   - **Start Command**: 
     ```bash
     uvicorn app:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type**: Free

4. **Deploy!** Render will auto-deploy on every push to main.

Your app will be live at: `https://research-doomscroll.onrender.com`

---

### Option 2: Railway.app (Also FREE)

1. **Go to [railway.app](https://railway.app)**

2. **"Start a New Project" → "Deploy from GitHub repo"**

3. **Select your repository**

4. **Railway auto-detects settings from `Procfile`**

5. **Add environment variables (optional):**
   - Go to Variables tab
   - Add any API keys if needed

6. **Deploy!** Gets a URL like: `https://research-doomscroll.up.railway.app`

---

### Option 3: Fly.io (More Control)

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login:**
   ```bash
   fly auth login
   ```

3. **Launch app:**
   ```bash
   fly launch
   ```

4. **Deploy:**
   ```bash
   fly deploy
   ```

---

## 📋 Files Included for Deployment

- ✅ `render.yaml` - Render.com configuration
- ✅ `Procfile` - Heroku/Railway configuration  
- ✅ `runtime.txt` - Python version specification
- ✅ `requirements.txt` - Python dependencies
- ✅ `nltk.txt` - NLTK data packages

---

## 🔧 Environment Variables (Optional)

If you have a Semantic Scholar API key:

1. In Render/Railway dashboard, go to "Environment Variables"
2. Add: `SEMANTIC_SCHOLAR_API_KEY=your_key_here`

---

## ⚠️ Important Notes

### Free Tier Limitations:

**Render.com:**
- ✅ 750 hours/month free
- ⚠️ Apps sleep after 15 min of inactivity
- ⏱️ First request after sleep takes ~30 seconds

**Railway.app:**
- ✅ $5 free credit monthly
- ✅ No auto-sleep
- ✅ Better performance

**Fly.io:**
- ✅ Good free tier
- ✅ 3 VMs included
- ⚠️ More complex setup

---

## 🎯 Recommended: Start with Render.com

**Why?**
- Easiest setup (literally 2 minutes)
- Auto-deploys from GitHub
- Free SSL certificate
- Good for demos and personal use

**When to upgrade?**
- If you need 24/7 uptime without sleep: Railway or paid Render
- If you need more control: Fly.io
- If you get lots of traffic: Consider paid tiers

---

## 🔄 Continuous Deployment

All options support auto-deployment:
- Push to GitHub → Automatically deploys
- No manual intervention needed
- See deployment logs in dashboard

---

## 📝 Post-Deployment Checklist

1. ✅ Test the live URL
2. ✅ Check that NLTK downloads work
3. ✅ Test paper search functionality
4. ✅ Test like/dislike persistence
5. ✅ Monitor logs for any errors

---

## 🆘 Troubleshooting

**Issue**: "Module not found"
- **Fix**: Check `requirements.txt` has all dependencies

**Issue**: "NLTK data not found"
- **Fix**: Ensure build command downloads NLTK data:
  ```bash
  python -c "import nltk; nltk.download('punkt_tab'); nltk.download('punkt')"
  ```

**Issue**: "Port binding error"
- **Fix**: Make sure start command uses: `--host 0.0.0.0 --port $PORT`

**Issue**: "App is slow"
- **Fix**: Free tiers sleep after inactivity. First request will be slow.

---

## 🎉 You're Ready to Deploy!

Pick an option above and follow the steps. In 5 minutes, your app will be live on the internet!
