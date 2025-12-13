# GroupMeet

GroupMeet is a lightweight web platform that matches Penn students into study groups based on class, availability, and study preferences, then uses quick feedback surveys to continuously improve match quality.

## Project Structure

```
group-meet/
├── backend/              # Flask backend application
├── frontend/             # React frontend application
├── data/                 # Data storage and samples
├── docs/                 # Documentation
├── scripts/              # Utility scripts
└── tests/                # Test suite
```

## Features

- **Penn CAS SSO Authentication**: Secure login using Penn's Central Authentication Service
- **Quality Control**: Enrollment verification via class rosters
- **Intelligent Matching**: Compatibility-based group formation using scikit-learn
- **Automated Email Notifications**: SendGrid integration for match distribution
- **Feedback Collection**: Post-match surveys to improve future matches
- **Admin Dashboard**: Platform statistics and management tools

## Tech Stack

### Backend
- **Flask**: Python web framework
- **Firebase Firestore**: Database for submissions, matches, and feedback
- **SendGrid**: Email service for notifications
- **scikit-learn**: Machine learning for group clustering
- **python-cas**: CAS authentication library

### Frontend
- **React**: UI framework
- **TypeScript**: Type-safe JavaScript
- **Vite**: Build tool and dev server
- **Axios**: HTTP client

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 18+
- Firebase account and project
- SendGrid account (optional, for email features)
- Penn CAS access

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables:
```bash
export SECRET_KEY="your-secret-key"
export CAS_SERVER_ROOT="https://alliance.seas.upenn.edu/~lumbroso/cgi-bin/cas/"
export FIREBASE_PROJECT_ID="your-firebase-project-id"
export FIREBASE_CREDENTIALS_PATH="path/to/firebase-credentials.json"
export SENDGRID_API_KEY="your-sendgrid-api-key"
export FROM_EMAIL="noreply@groupmeet.upenn.edu"
export CORS_ORIGINS="http://localhost:3000"
```

5. Run the server:
```bash
python app.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file:
```bash
VITE_API_URL=http://localhost:5000
```

4. Run development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## Configuration

### Environment Variables

#### Backend

- `SECRET_KEY`: Flask session secret key
- `CAS_SERVER_ROOT`: CAS server base URL (must end with `/`)
- `FIREBASE_PROJECT_ID`: Firebase project ID
- `FIREBASE_CREDENTIALS_PATH`: Path to Firebase service account JSON
- `SENDGRID_API_KEY`: SendGrid API key for email service
- `FROM_EMAIL`: From email address for notifications
- `CORS_ORIGINS`: Comma-separated list of allowed CORS origins
- `MIN_GROUP_SIZE`: Minimum group size (default: 3)
- `MAX_GROUP_SIZE`: Maximum group size (default: 5)

#### Frontend

- `VITE_API_URL`: Backend API URL

## API Documentation

### Authentication Endpoints

- `GET /auth/login` - Redirect to CAS login
- `GET /auth/logout` - Logout and clear session
- `GET /auth/callback` - CAS callback handler
- `GET /auth/status` - Check authentication status

### Submission Endpoints

- `POST /api/submissions` - Create new submission (requires auth)
- `GET /api/submissions` - Get user's submissions (requires auth)
- `GET /api/submissions/:id` - Get specific submission (requires auth)
- `DELETE /api/submissions/:id` - Delete submission (requires auth)

### Match Endpoints

- `GET /api/matches?course=COURSE_ID` - Get user's match for course (requires auth)
- `GET /api/matches/:id` - Get specific match (requires auth)
- `POST /api/matches/trigger` - Trigger matching (admin only)

### Feedback Endpoints

- `POST /api/feedback` - Submit feedback (requires auth)
- `GET /api/feedback?match_id=MATCH_ID` - Get feedback (requires auth)

### Admin Endpoints

- `GET /api/admin/stats` - Platform statistics (admin only)
- `GET /api/admin/submissions` - All submissions (admin only)
- `GET /api/admin/matches` - All matches (admin only)
- `POST /api/admin/roster/:course_id` - Upload class roster (admin only)

## Usage

### For Students

1. **Login**: Click "Login with PennKey" and authenticate via Penn CAS
2. **Submit Preferences**: Fill out the preference form with:
   - Course code
   - Availability slots
   - Study style preference
   - Learning goal
   - Preferred group size
3. **Get Matched**: Wait for matching to complete (admin-triggered)
4. **View Match**: Check dashboard for your assigned group
5. **Provide Feedback**: Rate your experience after meeting with your group

### For Admins

1. **Upload Roster**: Use admin endpoint to upload class rosters
2. **Trigger Matching**: Run matching algorithm for a course
3. **View Statistics**: Monitor platform usage and match quality

## Development

### Running Tests

Backend tests:
```bash
cd backend
pytest tests/
```

Frontend tests:
```bash
cd frontend
npm test
```

### Code Structure

- `backend/auth/` - CAS authentication module
- `backend/api/` - REST API routes
- `backend/src/qc/` - Quality control module
- `backend/src/aggregation/` - Matching algorithm
- `backend/src/services/` - Shared services (Firebase, Email)
- `backend/models/` - Data models
- `frontend/src/components/` - React components
- `frontend/src/services/` - API client and types
- `frontend/src/hooks/` - Custom React hooks

## Deployment

### Backend (Render/Heroku)

1. Set environment variables in deployment platform
2. Ensure `SECRET_KEY`, `CAS_SERVER_ROOT`, and Firebase credentials are configured
3. Deploy using `render.yaml` or Heroku Procfile

### Frontend (Vercel)

1. Set `VITE_API_URL` environment variable
2. Connect repository to Vercel
3. Deploy automatically on push

## Team

- Alexander Mehta (amehta26) - Project Management
- Brandon Yan (bdonyan) - Backend Development
- Connor Cummings (connorcc) - QC Module
- Nikki Liu (nikkiliu) - Aggregation Module

## License

This project is for academic use as part of the NETS course at the University of Pennsylvania.

## Acknowledgments

- CAS authentication adapted from [cas-flask-demo](https://github.com/jlumbroso/cas-flask-demo)
- Penn SEAS Alliance for CAS proxy access
