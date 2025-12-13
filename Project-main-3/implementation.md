# GroupMeet Implementation Plan

## Overview

This document outlines the complete implementation strategy for GroupMeet, a study group matching platform for Penn students. The implementation follows software engineering best practices including separation of concerns, RESTful API design, modular architecture, and secure authentication.

## Architecture Overview

### High-Level Architecture

```
┌─────────────┐
│   React     │  Frontend (Vercel)
│   Frontend  │
└──────┬──────┘
       │ HTTPS/REST API
       ↓
┌─────────────────────────────────────┐
│      Flask Backend (Render)         │
│  ┌──────────────────────────────┐   │
│  │  Authentication Layer        │   │
│  │  (CAS SSO Integration)       │   │
│  └──────────┬───────────────────┘   │
│             ↓                        │
│  ┌──────────────────────────────┐   │
│  │  API Routes                  │   │
│  │  - /auth/*                   │   │
│  │  - /api/submissions          │   │
│  │  - /api/matches              │   │
│  │  - /api/feedback             │   │
│  │  - /api/admin/*              │   │
│  └──────────┬───────────────────┘   │
│             ↓                        │
│  ┌──────────────────────────────┐   │
│  │  Business Logic Layer        │   │
│  │  - QC Module                 │   │
│  │  - Aggregation Module        │   │
│  │  - Email Service             │   │
│  └──────────┬───────────────────┘   │
│             ↓                        │
│  ┌──────────────────────────────┐   │
│  │  Data Access Layer           │   │
│  │  - Firebase Client           │   │
│  │  - Class Roster Service      │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
             ↓
┌─────────────────────────────┐
│   Firebase Realtime DB      │
│   - Submissions             │
│   - Matches                 │
│   - Feedback                │
│   - Class Rosters           │
└─────────────────────────────┘
```

## Project Structure

```
group-meet/
├── README.md
├── implementation.md              # This file
├── groupmeet.md                  # Project proposal
│
├── frontend/                      # React Frontend
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   │   ├── LoginButton.tsx
│   │   │   │   └── ProtectedRoute.tsx
│   │   │   ├── forms/
│   │   │   │   ├── PreferenceForm.tsx
│   │   │   │   └── FeedbackForm.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── StudentDashboard.tsx
│   │   │   │   └── AdminDashboard.tsx
│   │   │   └── common/
│   │   │       ├── LoadingSpinner.tsx
│   │   │       └── ErrorMessage.tsx
│   │   ├── services/
│   │   │   ├── api.ts            # API client with axios
│   │   │   ├── auth.ts           # Auth state management
│   │   │   └── types.ts          # TypeScript interfaces
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   └── useSubmission.ts
│   │   ├── utils/
│   │   │   └── constants.ts
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   └── .env.example
│
├── backend/                       # Flask Backend
│   ├── app.py                    # Flask app factory
│   ├── config.py                 # Configuration management
│   ├── requirements.txt
│   ├── Dockerfile                # Optional containerization
│   │
│   ├── auth/                     # Authentication Module
│   │   ├── __init__.py
│   │   ├── cas_client.py         # CAS client (adapted from cas-flask-demo)
│   │   ├── routes.py             # Auth routes (/login, /logout, /callback)
│   │   └── middleware.py         # Session management, auth decorators
│   │
│   ├── api/                      # REST API Routes
│   │   ├── __init__.py
│   │   ├── submissions.py        # POST/GET /api/submissions
│   │   ├── matches.py            # GET /api/matches
│   │   ├── feedback.py           # POST/GET /api/feedback
│   │   └── admin.py              # Admin endpoints (/api/admin/*)
│   │
│   ├── src/
│   │   ├── qc/                   # Quality Control Module
│   │   │   ├── __init__.py
│   │   │   ├── validators.py     # Enrollment verification
│   │   │   ├── roster_service.py # Class roster management
│   │   │   └── exceptions.py     # Custom QC exceptions
│   │   │
│   │   ├── aggregation/          # Aggregation/Matching Module
│   │   │   ├── __init__.py
│   │   │   ├── matcher.py        # Main matching algorithm
│   │   │   ├── clustering.py     # Group clustering logic
│   │   │   ├── scoring.py        # Compatibility scoring
│   │   │   └── exceptions.py
│   │   │
│   │   └── services/             # Shared Services
│   │       ├── __init__.py
│   │       ├── email_service.py  # SendGrid integration
│   │       ├── firebase_service.py # Firebase client wrapper
│   │       └── scheduler.py      # Match scheduling/triggers
│   │
│   ├── models/                   # Data Models
│   │   ├── __init__.py
│   │   ├── submission.py         # Submission data model
│   │   ├── match.py              # Match/group data model
│   │   └── user.py               # User profile model
│   │
│   └── utils/                    # Utilities
│       ├── __init__.py
│       ├── logging_config.py     # Logging setup
│       └── errors.py             # Error handlers
│
├── data/                         # Data Storage
│   ├── raw/                      # Raw input data
│   ├── sample-qc-input/          # QC test inputs
│   ├── sample-qc-output/         # QC test outputs
│   ├── sample-agg-input/         # Aggregation test inputs
│   ├── sample-agg-output/        # Aggregation test outputs
│   └── README.md                 # Data format documentation
│
├── tests/                        # Test Suite
│   ├── unit/
│   │   ├── test_qc.py
│   │   ├── test_aggregation.py
│   │   └── test_auth.py
│   ├── integration/
│   │   └── test_api.py
│   └── fixtures/
│       └── sample_data.py
│
├── docs/
│   ├── flow-diagram.pdf
│   ├── mockups/
│   └── api/
│       └── api_spec.md           # API documentation
│
└── scripts/                      # Utility Scripts
    ├── setup_roster.py           # Import class roster
    ├── run_matching.py           # Manual match trigger
    └── send_feedback_reminders.py
```

## API Design

### RESTful API Endpoints

#### Authentication Endpoints
```
GET  /auth/login          # Redirect to CAS login
GET  /auth/logout         # Logout and clear session
GET  /auth/callback       # CAS callback handler
GET  /auth/status         # Check current auth status
```

#### Submission Endpoints
```
POST   /api/submissions              # Create new submission (requires auth)
GET    /api/submissions              # Get user's submission (requires auth)
GET    /api/submissions/:id          # Get specific submission (requires auth)
DELETE /api/submissions/:id          # Delete submission (requires auth)
```

#### Match Endpoints
```
GET  /api/matches                    # Get user's assigned group (requires auth)
GET  /api/matches/:id                # Get specific match details (requires auth)
POST /api/matches/trigger            # Trigger matching (admin only)
```

#### Feedback Endpoints
```
POST /api/feedback                   # Submit feedback (requires auth)
GET  /api/feedback                   # Get user's feedback (requires auth)
GET  /api/feedback/:match_id         # Get feedback for specific match (requires auth)
```

#### Admin Endpoints
```
GET  /api/admin/stats                # Platform statistics (admin only)
GET  /api/admin/submissions          # All submissions (admin only)
GET  /api/admin/matches              # All matches (admin only)
GET  /api/admin/feedback             # All feedback (admin only)
POST /api/admin/roster/:course_id    # Upload/update roster (admin only)
```

### Request/Response Formats

#### Submission Creation (POST /api/submissions)
```json
// Request
{
  "course": "CIS1200",
  "availability": ["Mon_PM", "Tue_AM", "Wed_PM"],
  "study_style": "visual",
  "goal": "problem_sets",
  "preferred_group_size": 4
}

// Response (201 Created)
{
  "id": "sub_123456",
  "pennkey": "amehta26",
  "course": "CIS1200",
  "status": "pending",
  "created_at": "2025-11-13T10:00:00Z",
  "validated_at": null
}
```

#### Match Retrieval (GET /api/matches)
```json
// Response (200 OK)
{
  "match_id": "match_789",
  "group_id": 101,
  "course": "CIS1200",
  "members": [
    {
      "pennkey": "amehta26",
      "email": "amehta26@upenn.edu",
      "name": "Alexander Mehta"
    },
    {
      "pennkey": "bdonyan",
      "email": "bdonyan@upenn.edu",
      "name": "Brandon Yan"
    }
  ],
  "compatibility_score": 0.85,
  "suggested_meeting_time": "Mon_PM",
  "created_at": "2025-11-15T14:00:00Z"
}
```

#### Feedback Submission (POST /api/feedback)
```json
// Request
{
  "match_id": "match_789",
  "rating": 4,
  "comments": "Great group, very productive",
  "met_with_group": true,
  "would_meet_again": true
}

// Response (201 Created)
{
  "id": "fb_456",
  "match_id": "match_789",
  "pennkey": "amehta26",
  "rating": 4,
  "created_at": "2025-11-20T10:00:00Z"
}
```

## Authentication Implementation

### CAS SSO Integration (Adapted from cas-flask-demo)

The authentication system will integrate the `cas-flask-demo` approach with our Flask backend.

#### Key Components

1. **CAS Client (`backend/auth/cas_client.py`)**
   - Handles CAS ticket validation
   - Parses CAS XML response
   - Extracts PennKey and user attributes
   - Uses `python-cas` library or custom implementation based on cas-flask-demo

2. **Auth Routes (`backend/auth/routes.py`)**
   ```python
   @auth_bp.route('/login')
   def login():
       """Redirect to CAS login"""
       cas_url = f"{CAS_SERVER_ROOT}login.php"
       service_url = url_for('auth.callback', _external=True)
       redirect_url = f"{cas_url}?service={quote(service_url)}"
       return redirect(redirect_url)
   
   @auth_bp.route('/callback')
   def callback():
       """Handle CAS callback"""
       ticket = request.args.get('ticket')
       if not ticket:
           return jsonify({'error': 'No ticket provided'}), 400
       
       pennkey, attributes = cas_client.validate_ticket(ticket, request.url)
       session['pennkey'] = pennkey
       session['authenticated'] = True
       return redirect(url_for('frontend.dashboard'))
   
   @auth_bp.route('/logout')
   def logout():
       """Logout and clear session"""
       session.clear()
       cas_logout_url = f"{CAS_SERVER_ROOT}logout.php"
       return redirect(cas_logout_url)
   ```

3. **Auth Middleware (`backend/auth/middleware.py`)**
   ```python
   def require_auth(f):
       """Decorator to require authentication"""
       @wraps(f)
       def decorated_function(*args, **kwargs):
           if 'authenticated' not in session or not session['authenticated']:
               return jsonify({'error': 'Unauthorized'}), 401
           return f(*args, **kwargs)
       return decorated_function
   ```

4. **Configuration (`backend/config.py`)**
   ```python
   import os
   
   class Config:
       SECRET_KEY = os.environ.get('SECRET_KEY')
       CAS_SERVER_ROOT = os.environ.get('CAS_SERVER_ROOT', 
           'https://alliance.seas.upenn.edu/~lumbroso/cgi-bin/cas/')
       
       # Firebase
       FIREBASE_CONFIG = {
           'apiKey': os.environ.get('FIREBASE_API_KEY'),
           'projectId': os.environ.get('FIREBASE_PROJECT_ID'),
           # ... other Firebase config
       }
       
       # SendGrid
       SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
       FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@groupmeet.upenn.edu')
   ```

## QC Module Implementation

### Purpose
Validate that authenticated users are enrolled in the course they're submitting for.

### Structure (`backend/src/qc/`)

1. **Roster Service (`roster_service.py`)**
   ```python
   class RosterService:
       def __init__(self, firebase_client):
           self.db = firebase_client
       
       def load_roster(self, course_id: str) -> List[str]:
           """Load class roster from Firebase"""
           roster_ref = self.db.collection('rosters').document(course_id)
           roster = roster_ref.get()
           return roster.get('pennkeys', [])
       
       def is_enrolled(self, pennkey: str, course_id: str) -> bool:
           """Check if pennkey is enrolled in course"""
           roster = self.load_roster(course_id)
           return pennkey in roster
   ```

2. **Validators (`validators.py`)**
   ```python
   class SubmissionValidator:
       def __init__(self, roster_service):
           self.roster_service = roster_service
       
       def validate_submission(self, submission: dict, pennkey: str) -> ValidationResult:
           """Validate submission"""
           errors = []
           
           # Check enrollment
           if not self.roster_service.is_enrolled(pennkey, submission['course']):
               errors.append('Not enrolled in course')
           
           # Check if already submitted
           if self._has_existing_submission(pennkey, submission['course']):
               errors.append('Already submitted for this course')
           
           # Validate availability format
           if not self._validate_availability(submission['availability']):
               errors.append('Invalid availability format')
           
           return ValidationResult(
               is_valid=len(errors) == 0,
               errors=errors,
               sanitized_data=self._sanitize(submission) if len(errors) == 0 else None
           )
   ```

3. **Integration with API**
   ```python
   @submissions_bp.route('/api/submissions', methods=['POST'])
   @require_auth
   def create_submission():
       pennkey = session['pennkey']
       data = request.get_json()
       
       validator = SubmissionValidator(roster_service)
       result = validator.validate_submission(data, pennkey)
       
       if not result.is_valid:
           return jsonify({'errors': result.errors}), 400
       
       # Store validated submission
       submission = firebase_service.create_submission({
           **result.sanitized_data,
           'pennkey': pennkey,
           'status': 'validated',
           'validated_at': datetime.utcnow().isoformat()
       })
       
       return jsonify(submission), 201
   ```

## Aggregation Module Implementation

### Purpose
Match students into optimal study groups based on compatibility scores.

### Matching Algorithm

1. **Compatibility Scoring (`backend/src/aggregation/scoring.py`)**
   ```python
   class CompatibilityScorer:
       def calculate_compatibility(self, student1: dict, student2: dict) -> float:
           """Calculate compatibility score between two students"""
           score = 0.0
           
           # Availability overlap (40% weight)
           avail_overlap = len(set(student1['availability']) & set(student2['availability']))
           max_avail = max(len(student1['availability']), len(student2['availability']))
           score += 0.4 * (avail_overlap / max_avail if max_avail > 0 else 0)
           
           # Study style match (30% weight)
           if student1['study_style'] == student2['study_style']:
               score += 0.3
           
           # Goal alignment (30% weight)
           if student1['goal'] == student2['goal']:
               score += 0.3
           
           return score
   ```

2. **Clustering Algorithm (`backend/src/aggregation/clustering.py`)**
   ```python
   from sklearn.cluster import AgglomerativeClustering
   import numpy as np
   
   class GroupMatcher:
       def __init__(self, scorer, min_group_size=3, max_group_size=5):
           self.scorer = scorer
           self.min_group_size = min_group_size
           self.max_group_size = max_group_size
       
       def match_students(self, validated_submissions: List[dict], course_id: str) -> List[dict]:
           """Match students into groups"""
           # Build compatibility matrix
           n = len(validated_submissions)
           compatibility_matrix = np.zeros((n, n))
           
           for i in range(n):
               for j in range(i+1, n):
                   compat = self.scorer.calculate_compatibility(
                       validated_submissions[i],
                       validated_submissions[j]
                   )
                   compatibility_matrix[i][j] = compat
                   compatibility_matrix[j][i] = compat
           
           # Use hierarchical clustering
           n_clusters = max(1, n // self.max_group_size)
           clustering = AgglomerativeClustering(
               n_clusters=n_clusters,
               linkage='average',
               affinity='precomputed'
           )
           labels = clustering.fit_predict(1 - compatibility_matrix)  # Convert to distance
           
           # Group by cluster
           groups = {}
           for idx, label in enumerate(labels):
               if label not in groups:
                   groups[label] = []
               groups[label].append(validated_submissions[idx])
           
           # Validate group sizes and split/merge as needed
           final_groups = self._adjust_group_sizes(groups)
           
           return [self._format_group(group, course_id) for group in final_groups]
   ```

3. **Match Execution (`backend/src/aggregation/matcher.py`)**
   ```python
   class MatchOrchestrator:
       def __init__(self, firebase_service, email_service, matcher):
           self.db = firebase_service
           self.email = email_service
           self.matcher = matcher
       
       def run_matching(self, course_id: str, deadline: datetime = None) -> dict:
           """Execute matching for a course"""
           # Fetch all validated submissions for course
           submissions = self.db.get_validated_submissions(course_id)
           
           if len(submissions) < self.matcher.min_group_size:
               raise InsufficientParticipantsError(
                   f"Need at least {self.matcher.min_group_size} participants"
               )
           
           # Run matching algorithm
           groups = self.matcher.match_students(submissions, course_id)
           
           # Store matches in Firebase
           match_ids = []
           for group in groups:
               match_id = self.db.create_match(group)
               match_ids.append(match_id)
               
               # Send emails to group members
               self.email.send_group_intro_email(group)
           
           return {
               'course_id': course_id,
               'matches_created': len(match_ids),
               'match_ids': match_ids,
               'timestamp': datetime.utcnow().isoformat()
           }
   ```

## Email Service Implementation

### Purpose
Send automated emails for match notifications and feedback reminders.

### Structure (`backend/src/services/email_service.py`)

```python
import sendgrid
from sendgrid.helpers.mail import Mail

class EmailService:
    def __init__(self, api_key: str, from_email: str):
        self.sg = sendgrid.SendGridAPIClient(api_key=api_key)
        self.from_email = from_email
    
    def send_group_intro_email(self, group: dict):
        """Send introduction email to all group members"""
        for member in group['members']:
            message = Mail(
                from_email=self.from_email,
                to_emails=member['email'],
                subject=f"Your {group['course']} Study Group is Ready!",
                html_content=self._generate_group_intro_html(group, member)
            )
            self.sg.send(message)
    
    def send_feedback_reminder(self, match: dict, days_after: int = 5):
        """Send feedback reminder after match"""
        for member in match['members']:
            message = Mail(
                from_email=self.from_email,
                to_emails=member['email'],
                subject="How did your study group go?",
                html_content=self._generate_feedback_reminder_html(match, member)
            )
            self.sg.send(message)
    
    def _generate_group_intro_html(self, group: dict, member: dict) -> str:
        """Generate HTML email template"""
        # Implementation for email template
        pass
```

## Frontend Implementation

### React Component Structure

1. **Authentication Flow**
   - `LoginButton.tsx`: Redirects to `/auth/login`
   - `ProtectedRoute.tsx`: Wraps routes requiring auth
   - `useAuth.ts`: Custom hook managing auth state

2. **Preference Form (`PreferenceForm.tsx`)**
   - Multi-step form for course selection, availability, preferences
   - Real-time validation
   - Submit to `/api/submissions`

3. **Dashboard (`StudentDashboard.tsx`)**
   - Show user's submission status
   - Display matched group when available
   - Link to feedback form

4. **Admin Dashboard (`AdminDashboard.tsx`)**
   - View all submissions
   - Trigger matching manually
   - View statistics and feedback

### API Client (`frontend/src/services/api.ts`)

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  withCredentials: true,  // Important for session cookies
});

// Request interceptor for auth
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.location.href = '/auth/login';
    }
    return Promise.reject(error);
  }
);

export const submissionsAPI = {
  create: (data: SubmissionData) => api.post('/api/submissions', data),
  get: () => api.get('/api/submissions'),
};

export const matchesAPI = {
  get: () => api.get('/api/matches'),
};

export const feedbackAPI = {
  create: (data: FeedbackData) => api.post('/api/feedback', data),
  get: () => api.get('/api/feedback'),
};
```

## Data Models

### Submission Model
```python
@dataclass
class Submission:
    id: str
    pennkey: str
    course: str
    availability: List[str]
    study_style: str
    goal: str
    preferred_group_size: int
    status: str  # pending, validated, matched
    created_at: datetime
    validated_at: Optional[datetime]
```

### Match Model
```python
@dataclass
class Match:
    match_id: str
    group_id: int
    course: str
    members: List[Member]
    compatibility_score: float
    suggested_meeting_time: str
    created_at: datetime
    feedback_sent: bool
    feedback_due_date: datetime
```

## Security Considerations

1. **Authentication**
   - All API endpoints (except `/auth/login`) require authentication
   - Session-based auth with secure cookies
   - CAS ticket validation on backend

2. **Authorization**
   - Users can only access their own data
   - Admin endpoints require admin role check
   - PennKey validation prevents spoofing

3. **Data Validation**
   - Input validation on both frontend and backend
   - SQL injection prevention (using Firebase eliminates SQL)
   - XSS prevention via React's built-in escaping

4. **Rate Limiting**
   - Implement rate limiting on submission endpoints
   - Prevent spam/abuse

## Testing Strategy

### Unit Tests
- QC module validation logic
- Aggregation scoring algorithms
- CAS client ticket validation

### Integration Tests
- Full submission → QC → aggregation flow
- Auth flow end-to-end
- Email service integration

### End-to-End Tests
- Complete user journey: login → submit → match → feedback

## Deployment Strategy

### Backend (Render/Heroku)
1. Set environment variables:
   - `SECRET_KEY`
   - `CAS_SERVER_ROOT`
   - `FIREBASE_API_KEY`, `FIREBASE_PROJECT_ID`, etc.
   - `SENDGRID_API_KEY`
2. Deploy using `render.yaml` or Heroku Procfile
3. Configure CORS for frontend domain

### Frontend (Vercel)
1. Set `REACT_APP_API_URL` to backend URL
2. Deploy via GitHub integration
3. Configure redirects for SPA routing

### Database (Firebase)
1. Set up Firebase project
2. Configure security rules
3. Initialize collections: `submissions`, `matches`, `feedback`, `rosters`

## Environment Variables

### Backend
```
SECRET_KEY=<flask-secret-key>
CAS_SERVER_ROOT=https://alliance.seas.upenn.edu/~lumbroso/cgi-bin/cas/
FIREBASE_API_KEY=<firebase-api-key>
FIREBASE_PROJECT_ID=<firebase-project-id>
FIREBASE_STORAGE_BUCKET=<firebase-storage-bucket>
SENDGRID_API_KEY=<sendgrid-api-key>
FROM_EMAIL=noreply@groupmeet.upenn.edu
ENVIRONMENT=production
```

### Frontend
```
REACT_APP_API_URL=https://groupmeet-backend.onrender.com
```

## Development Workflow

### Local Development Setup

1. **Backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   export SECRET_KEY="dev-secret-key"
   export CAS_SERVER_ROOT="https://alliance.seas.upenn.edu/~lumbroso/cgi-bin/cas/"
   # ... set other env vars
   python app.py
   ```

2. **Frontend**
   ```bash
   cd frontend
   npm install
   npm start  # Runs on http://localhost:3000
   ```

3. **Testing**
   ```bash
   # Run backend tests
   cd backend
   pytest tests/

   # Run frontend tests
   cd frontend
   npm test
   ```

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)
- [ ] Set up project structure
- [ ] Implement CAS authentication (integrate cas-flask-demo)
- [ ] Set up Firebase connection
- [ ] Create basic API routes structure
- [ ] Deploy backend and frontend to staging

### Phase 2: Submission & QC (Week 1-2)
- [ ] Build preference form (React)
- [ ] Implement QC module (enrollment validation)
- [ ] Create submission API endpoints
- [ ] Test submission flow end-to-end

### Phase 3: Aggregation (Week 2)
- [ ] Implement compatibility scoring
- [ ] Build clustering/matching algorithm
- [ ] Create match API endpoints
- [ ] Test matching with sample data

### Phase 4: Distribution & Feedback (Week 2-3)
- [ ] Integrate SendGrid email service
- [ ] Build feedback form
- [ ] Create feedback API endpoints
- [ ] Implement feedback reminder scheduling

### Phase 5: Admin & Polish (Week 3-4)
- [ ] Build admin dashboard
- [ ] Add statistics/analytics endpoints
- [ ] Implement roster upload functionality
- [ ] Polish UI/UX
- [ ] Comprehensive testing

## Monitoring & Logging

1. **Application Logging**
   - Use Python `logging` module
   - Log all API requests with user context
   - Log errors with stack traces

2. **Error Tracking**
   - Consider Sentry for error monitoring
   - Track failed authentications
   - Monitor matching failures

3. **Metrics**
   - Track submission counts
   - Monitor match success rates
   - Track feedback response rates

## Future Enhancements (Post-MVP)

1. **Advanced Matching**
   - Machine learning-based compatibility
   - Historical feedback integration
   - Multi-round matching

2. **Features**
   - Calendar integration
   - In-app messaging
   - Group scheduling tools

3. **Analytics**
   - Match quality predictions
   - Student satisfaction trends
   - Course-specific insights

