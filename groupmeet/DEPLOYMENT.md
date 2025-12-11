# GroupMeet Deployment Guide

This guide covers options for deploying your GroupMeet application to a public URL.

## Deployment Options

### Option 1: Railway (Recommended - Easiest Full-Stack)

**Best for:** Quick deployment with minimal configuration

**Steps:**
1. Sign up at [railway.app](https://railway.app) (free tier available)
2. Install Railway CLI: `npm i -g @railway/cli`
3. In your project root, run: `railway login`
4. Run: `railway init`
5. Set environment variables in Railway dashboard:
   - `DB_TYPE=memory` (or configure Firestore/Sheets)
   - `DEV_BYPASS_AUTH=false` (for production)
   - `SECRET_KEY=<generate-a-secure-key>`
   - `CAS_SERVER_ROOT=<your-cas-server-url>`
6. Deploy: `railway up`
7. Railway provides a public URL automatically

**Pros:**
- Free tier available
- Automatic HTTPS
- Easy environment variable management
- Supports both frontend and backend

**Cons:**
- Free tier has usage limits

---

### Option 2: Render (Free Tier Available)

**Best for:** Simple deployment with free hosting

**Steps:**
1. Sign up at [render.com](https://render.com)
2. Create a new "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Build Command:** `cd groupmeet/backend && pip install -r requirements.txt`
   - **Start Command:** `cd groupmeet/backend && python app.py`
   - **Environment:** Python 3
5. Set environment variables in Render dashboard
6. For frontend: Create a separate "Static Site" pointing to `groupmeet/frontend`
7. Update CORS in `app.py` to allow your Render frontend URL

**Pros:**
- Free tier available
- Automatic HTTPS
- Easy Git-based deployment

**Cons:**
- Free tier spins down after inactivity
- Need separate services for frontend/backend

---

### Option 3: Vercel (Frontend) + Railway/Render (Backend)

**Best for:** Optimized frontend hosting

**Frontend (Vercel):**
1. Sign up at [vercel.com](https://vercel.com)
2. Install Vercel CLI: `npm i -g vercel`
3. In `groupmeet/frontend` directory: `vercel`
4. Follow prompts to deploy

**Backend (Railway/Render):**
- Follow Option 1 or 2 above

**Update CORS:**
- In `backend/app.py`, update CORS origins to include your Vercel URL

**Pros:**
- Excellent frontend performance
- Free tier
- Automatic HTTPS and CDN

**Cons:**
- Need to manage two services
- CORS configuration required

---

### Option 4: Heroku (Classic Option)

**Best for:** Traditional full-stack deployment

**Steps:**
1. Sign up at [heroku.com](https://heroku.com)
2. Install Heroku CLI: `brew install heroku/brew/heroku` (Mac)
3. Login: `heroku login`
4. Create app: `heroku create groupmeet-app`
5. Set environment variables:
   ```bash
   heroku config:set DB_TYPE=memory
   heroku config:set DEV_BYPASS_AUTH=false
   heroku config:set SECRET_KEY=$(openssl rand -hex 32)
   ```
6. Create `Procfile` in project root:
   ```
   web: cd groupmeet/backend && python app.py
   ```
7. Deploy: `git push heroku main`

**Pros:**
- Well-established platform
- Good documentation
- Free tier (with limitations)

**Cons:**
- Free tier no longer available for new accounts
- More complex setup

---

## Pre-Deployment Checklist

### 1. Update Configuration

**In `backend/config.py`:**
- Set `DEV_BYPASS_AUTH=False` for production
- Generate a secure `SECRET_KEY`
- Configure `CAS_SERVER_ROOT` for production CAS server
- Set `BASE_URL` to your production URL

**In `frontend/auth.js` and `frontend/dashboard.js`:**
- Update `API_BASE` to point to your production backend URL

### 2. Environment Variables

Set these in your hosting platform:
```
DB_TYPE=memory  # or firestore/sheets
DEV_BYPASS_AUTH=false
SECRET_KEY=<generate-secure-random-key>
CAS_SERVER_ROOT=https://your-cas-server-url
BASE_URL=https://your-frontend-url
MIN_GROUP_SIZE=3
MAX_GROUP_SIZE=5
```

### 3. CORS Configuration

Update `backend/app.py` CORS origins:
```python
CORS(app, origins=["https://your-frontend-url.com"], supports_credentials=True)
```

### 4. Database Setup (Optional)

For production, consider:
- **Firestore:** Set up Firebase project and add credentials
- **Google Sheets:** Set up service account and share sheet

### 5. Frontend Build (If Needed)

Some platforms require building. If so:
- Ensure all paths are relative (not absolute)
- Update API endpoints to use environment variables

---

## Quick Start: Railway Deployment

1. **Install Railway CLI:**
   ```bash
   npm i -g @railway/cli
   ```

2. **Login:**
   ```bash
   railway login
   ```

3. **Initialize:**
   ```bash
   cd /Users/brandonyan/Desktop/Project/groupmeet
   railway init
   ```

4. **Set Environment Variables:**
   ```bash
   railway variables set DB_TYPE=memory
   railway variables set DEV_BYPASS_AUTH=false
   railway variables set SECRET_KEY=$(openssl rand -hex 32)
   ```

5. **Create `Procfile` in `groupmeet/` directory:**
   ```
   web: cd backend && python app.py
   ```

6. **Deploy:**
   ```bash
   railway up
   ```

7. **Get URL:**
   Railway will provide a public URL like `https://your-app.railway.app`

---

## Post-Deployment

1. **Test the deployment:**
   - Visit your public URL
   - Test login flow
   - Test form submission
   - Verify groups are created

2. **Monitor:**
   - Check logs in your hosting platform
   - Monitor error rates
   - Test with multiple users

3. **Custom Domain (Optional):**
   - Most platforms support custom domains
   - Update DNS records as instructed by platform
   - Update `BASE_URL` and CORS settings

---

## Troubleshooting

**CORS Errors:**
- Ensure frontend URL is in CORS origins
- Check `supports_credentials=True` is set

**Session Issues:**
- Verify `SECRET_KEY` is set and consistent
- Check cookie settings (secure, sameSite)

**Database Issues:**
- Verify database credentials if using Firestore/Sheets
- Check database connection in logs

**Static Files:**
- Ensure frontend files are being served correctly
- Check file paths are relative, not absolute

---

## Recommended Setup for MVP

**For quick MVP deployment:**
1. Use **Railway** for backend (easiest)
2. Use **Vercel** for frontend (best performance)
3. Keep `DB_TYPE=memory` for now (upgrade later)
4. Set `DEV_BYPASS_AUTH=false` for production
5. Configure CAS server URL for PennKey login

This gives you a production-ready deployment in ~30 minutes.

