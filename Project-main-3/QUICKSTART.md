# GroupMeet Quick Start Guide

This guide will help you get the GroupMeet application up and running quickly.

## Prerequisites

- Python 3.9+ installed
- Node.js 18+ installed
- Firebase account and project set up
- SendGrid account (optional, for email features)

## Quick Setup

### 1. Backend Setup (5 minutes)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set required environment variables
export SECRET_KEY="dev-secret-key-12345"
export CAS_SERVER_ROOT="https://alliance.seas.upenn.edu/~lumbroso/cgi-bin/cas/"
export FIREBASE_PROJECT_ID="your-firebase-project-id"
export FIREBASE_CREDENTIALS_PATH="path/to/firebase-credentials.json"
export SENDGRID_API_KEY="your-sendgrid-key"  # Optional
export FROM_EMAIL="noreply@groupmeet.upenn.edu"
export CORS_ORIGINS="http://localhost:3000"

# Run backend
python app.py
```

Backend should be running on `http://localhost:5000`

### 2. Frontend Setup (3 minutes)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:5000" > .env

# Run frontend
npm run dev
```

Frontend should be running on `http://localhost:3000`

### 3. Firebase Setup

1. Create a Firebase project at https://console.firebase.google.com
2. Enable Firestore Database
3. Download service account credentials JSON
4. Set `FIREBASE_CREDENTIALS_PATH` to the path of the JSON file
5. Set `FIREBASE_PROJECT_ID` to your Firebase project ID

### 4. Upload Class Roster (Admin)

Once the backend is running, you can upload a class roster using the admin API:

```bash
curl -X POST http://localhost:5000/api/admin/roster/CIS1200 \
  -H "Content-Type: application/json" \
  -d '{
    "pennkeys": ["student1", "student2", "student3"]
  }' \
  --cookie "session=YOUR_SESSION_COOKIE"
```

## Testing the Application

### 1. Test Authentication

1. Open `http://localhost:3000` in your browser
2. Click "Login with PennKey"
3. Authenticate via Penn CAS
4. You should be redirected back to the dashboard

### 2. Test Submission

1. On the dashboard, click "Submit Preferences"
2. Fill out the preference form:
   - Course code (e.g., CIS1200)
   - Availability slots (select multiple)
   - Study style
   - Goal
   - Preferred group size
3. Submit the form
4. You should see a success message

### 3. Test Matching (Admin)

1. Ensure you have at least 3-5 submissions for a course
2. Trigger matching via the admin API:
```bash
curl -X POST http://localhost:5000/api/matches/trigger \
  -H "Content-Type: application/json" \
  -d '{"course_id": "CIS1200"}' \
  --cookie "session=YOUR_SESSION_COOKIE"
```

### 4. Check Match Results

1. Go to "My Status" tab on the dashboard
2. Click "Check for Match"
3. You should see your assigned group if matching was successful

## Common Issues

### Backend won't start

- **Issue**: Import errors
- **Solution**: Make sure you're in the project root when running `python app.py`, or use `python -m backend.app`

### Firebase connection fails

- **Issue**: "Firebase initialization failed"
- **Solution**: Check that `FIREBASE_CREDENTIALS_PATH` points to a valid JSON file and `FIREBASE_PROJECT_ID` is correct

### CORS errors

- **Issue**: Frontend can't connect to backend
- **Solution**: Make sure `CORS_ORIGINS` includes `http://localhost:3000` and backend is running

### CAS authentication fails

- **Issue**: "Authentication failed" after CAS login
- **Solution**: Verify `CAS_SERVER_ROOT` is correct and accessible. Test the CAS server URL directly.

## Next Steps

1. Review the `implementation.md` for architecture details
2. Check `README.md` for full documentation
3. Customize configuration for your environment
4. Deploy to production (Render/Heroku for backend, Vercel for frontend)

## Getting Help

- Check the main `README.md` for detailed documentation
- Review `implementation.md` for architecture and design decisions
- Check backend and frontend specific READMEs in their directories

