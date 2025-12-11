# Authentication Setup Guide

## Overview

GroupMeet supports two authentication modes:

1. **Development Mode**: Manual username login (for local testing)
2. **Production Mode**: PennKey/CAS authentication (for deployed app)

## Development Mode (Local Testing)

### How to Enable

**Option 1: Environment Variable (Recommended)**
```bash
cd groupmeet/backend
export DEV_BYPASS_AUTH=true
python3 app.py
```

**Option 2: Modify config.py temporarily**
Change line 47 in `backend/config.py`:
```python
DEV_BYPASS_AUTH = os.environ.get('DEV_BYPASS_AUTH', 'True').lower() == 'true'  # Changed False to True
```

### How It Works

- When `DEV_BYPASS_AUTH=true`, the home page shows a **username input form** instead of "Login with PennKey"
- Users can enter any username (e.g., "alice", "bob", "charlie")
- No password required (dev mode only)
- Perfect for testing group matching with multiple users
- A yellow "🔧 DEV MODE" indicator appears in the top-right corner

### Testing Multiple Users

1. Start backend with `DEV_BYPASS_AUTH=true`
2. Open the app in your browser
3. Enter username "alice" and login
4. Join a group for a course (e.g., CIS1200)
5. Open an **incognito/private window** (or different browser)
6. Enter username "bob" and login
7. Join the same course (CIS1200)
8. Repeat with "charlie"
9. After 3+ users join the same course, matching happens automatically!

## Production Mode (PennKey/CAS)

### How to Enable

**Option 1: Environment Variable**
```bash
cd groupmeet/backend
export DEV_BYPASS_AUTH=false
python3 app.py
```

**Option 2: Don't set the variable (defaults to False)**
```bash
cd groupmeet/backend
python3 app.py
```

### How It Works

- Home page shows "Login with PennKey" button
- Clicking redirects to Penn CAS server
- User logs in with PennKey credentials
- CAS redirects back to your app
- User is authenticated and can use the dashboard

### Important: Hosting Requirement

**The CAS server will reject `localhost` URLs** (you saw the 409 error).

To use PennKey authentication, you need to:

1. **Host your app on a real domain** (e.g., `groupmeet.upenn.edu`)
2. **Register the domain** with Penn CAS administrators
3. **Get it whitelisted** as an allowed service URL
4. **Update `BASE_URL` and callback URLs** to use the real domain

Once whitelisted, CAS will accept redirects to your domain and authentication will work.

### Alternative: Use ngrok for Testing

If you want to test CAS locally before hosting:

1. Install ngrok: `brew install ngrok` (Mac) or download from ngrok.com
2. Start your backend: `python3 app.py`
3. In another terminal: `ngrok http 5000`
4. Copy the ngrok URL (e.g., `https://abc123.ngrok.io`)
5. Update your CAS callback URL to use the ngrok URL
6. Register the ngrok URL with CAS administrators (if possible)

## Quick Reference

| Mode | Setting | Login Method | Use Case |
|------|---------|--------------|----------|
| Dev | `DEV_BYPASS_AUTH=true` | Username input | Local testing, multiple users |
| Production | `DEV_BYPASS_AUTH=false` | PennKey/CAS | Deployed app, real users |

## Server Startup Messages

When you start the backend, you'll see:

**Development Mode:**
```
🔧 DEVELOPMENT MODE: CAS authentication BYPASSED
   Users can login with username/email (no password)
   Set DEV_BYPASS_AUTH=false for production (PennKey/CAS)
```

**Production Mode:**
```
🔐 PRODUCTION MODE: Using PennKey/CAS authentication
   Set DEV_BYPASS_AUTH=true for development mode
```

## Troubleshooting

**"409 Conflict" error when clicking PennKey login:**
- This means CAS doesn't accept `localhost` URLs
- Use dev mode (`DEV_BYPASS_AUTH=true`) for local testing
- Or host on a real domain and get it whitelisted

**Can't test with multiple users:**
- Make sure dev mode is enabled
- Use incognito windows or different browsers
- Each window = different session = different user

**Dev login form not showing:**
- Check that `DEV_BYPASS_AUTH=true` is set
- Restart the backend server
- Check backend logs for mode confirmation
- Hard refresh browser (Cmd+Shift+R)

