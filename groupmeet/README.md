# GroupMeet MVP

A lightweight study-group matching web platform that helps students find compatible study partners based on course, availability, and study preferences.

## 📋 Features

- **Student Form Submission**: Collect student information including course, availability, and study preferences
- **Matching Algorithm**: Rule-based matching that groups students by course, availability overlap, and preference alignment
- **Quality Control**: Validates submissions and runs attention checks
- **Feedback Aggregation**: Processes and aggregates feedback ratings
- **Admin Dashboard**: View submissions and generate matches
- **Email Notifications**: Simulated email system (console-based for MVP)

## 🏗️ Architecture

### Directory Structure

```
groupmeet/
├── frontend/
│   ├── index.html      # Main HTML page
│   ├── form.js         # Form submission logic
│   ├── results.js      # Results page logic
│   └── admin.js        # Admin dashboard logic
├── backend/
│   ├── app.py          # Flask application
│   ├── config.py       # Configuration management
│   ├── db.py           # Database abstraction layer
│   ├── matching.py     # Matching algorithm
│   ├── emailer.py      # Email delivery system
│   ├── qc/
│   │   └── quality_control.py  # QC module
│   └── aggregation/
│       └── aggregate.py        # Aggregation module
├── data/
│   ├── sample-qc-input.json
│   ├── sample-qc-output.json
│   ├── sample-agg-input.json
│   └── sample-agg-output.json
└── README.md
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd groupmeet/backend
   ```

2. **Install dependencies:**
   ```bash
   pip install flask flask-cors
   ```

   For production databases (optional):
   ```bash
   # For Firestore
   pip install firebase-admin
   
   # For Google Sheets
   pip install gspread google-auth
   
   # For SendGrid email
   pip install sendgrid
   ```

3. **Set environment variables (optional):**
   ```bash
   export DB_TYPE=memory  # Options: memory, firestore, sheets
   export EMAIL_PROVIDER=console  # Options: console, sendgrid, smtp
   export MIN_GROUP_SIZE=3
   export MAX_GROUP_SIZE=5
   ```

4. **Run the backend server:**
   ```bash
   python app.py
   ```

   The server will start on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd groupmeet/frontend
   ```

2. **Serve the files:**
   
   Option 1: Using Python's built-in server:
   ```bash
   python -m http.server 3000
   ```
   
   Option 2: Using Node.js http-server:
   ```bash
   npx http-server -p 3000
   ```
   
   Option 3: Open `index.html` directly in a browser (may have CORS issues)

3. **Access the application:**
   Open `http://localhost:3000` in your browser

## 📡 API Endpoints

### POST /submit
Submit a new student form.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "course": "CIS1200",
  "availability": ["Monday 2-4pm", "Wednesday 3-5pm"],
  "study_preference": "PSets",
  "commitment_confirmed": true
}
```

**Response:**
```json
{
  "status": "ok",
  "id": "uuid-here"
}
```

### GET /submissions
Get all submissions (admin endpoint).

**Response:**
```json
{
  "status": "ok",
  "count": 10,
  "submissions": [...]
}
```

### POST /match
Run the matching algorithm.

**Request Body (optional):**
```json
{
  "course": "CIS1200"
}
```

**Response:**
```json
{
  "status": "ok",
  "matches_created": 3,
  "unmatched_count": 2,
  "matches": [...],
  "unmatched_students": [...]
}
```

### GET /results/<student_id>
Get match results for a specific student.

**Response:**
```json
{
  "student": {...},
  "group_members": [...],
  "availability_overlap": 0.75,
  "preference_alignment": 1.0,
  "avg_compatibility": 0.825
}
```

### POST /feedback
Submit feedback for a match.

**Request Body:**
```json
{
  "match_id": "uuid",
  "student_id": "uuid",
  "rating": 5,
  "comments": "Great group!"
}
```

## 🧪 Testing

### Test Flow

1. **Start the backend:**
   ```bash
   cd groupmeet/backend
   python app.py
   ```

2. **Start the frontend:**
   ```bash
   cd groupmeet/frontend
   python -m http.server 3000
   ```

3. **Submit a form:**
   - Open `http://localhost:3000`
   - Fill out the form
   - Submit

4. **View submissions (Admin):**
   - Click "Admin Dashboard"
   - View all submissions

5. **Generate matches:**
   - Click "Generate Matches"
   - Check console for email notifications

6. **View results:**
   - Use the submission ID from step 3
   - Navigate to `http://localhost:3000/results/<submission_id>`

### Sample cURL Commands

**Submit a form:**
```bash
curl -X POST http://localhost:5000/submit \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Smith",
    "email": "alice@example.com",
    "course": "CIS1200",
    "availability": ["Monday 2-4pm", "Wednesday 3-5pm"],
    "study_preference": "PSets",
    "commitment_confirmed": true
  }'
```

**Get all submissions:**
```bash
curl http://localhost:5000/submissions
```

**Run matching:**
```bash
curl -X POST http://localhost:5000/match \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Get results:**
```bash
curl http://localhost:5000/results/<student_id>
```

## 🔧 Configuration

### Database Options

1. **In-Memory (Default)**: No setup required, data lost on restart
2. **Firestore**: Requires Firebase project and credentials
3. **Google Sheets**: Requires Google Cloud credentials and sheet ID

### Email Providers

1. **Console (Default)**: Prints emails to console
2. **SendGrid**: Requires API key
3. **SMTP**: Requires SMTP server credentials

## 📊 Matching Algorithm

The matching algorithm uses a greedy approach:

1. **Group by course**: Students are first grouped by their course
2. **Compute compatibility**: For each pair, compute:
   - Availability overlap (Jaccard similarity): `intersection / union`
   - Preference alignment: `1.0` if same, `0.0` if different
   - Final score: `0.7 * availability_overlap + 0.3 * preference_alignment`
3. **Form groups**: Greedily form groups of size 3-5
4. **Handle overflow**: Unmatched students are placed in an overflow bucket

## 🔍 Quality Control

The QC module validates:
- Required fields (name, email, course, availability, preference)
- Email format
- At least one availability slot
- Valid study preference
- Commitment confirmation

## 📈 Aggregation

The aggregation module computes:
- Mean rating
- Median rating
- Sample size (n)
- Confidence score (based on sample size and variance)
- Rating distribution

## 🎯 Future Enhancements

- Authentication system
- Real email delivery
- Database persistence
- Advanced matching algorithms
- Feedback dashboard
- Student profiles
- Group chat functionality

## 📝 License

This is an MVP prototype. Use as needed for development and testing.

## 🤝 Contributing

This is a working MVP. Feel free to extend and improve!

---

**Note**: This MVP uses in-memory storage by default. Data will be lost when the server restarts. For production, configure Firestore or Google Sheets.

