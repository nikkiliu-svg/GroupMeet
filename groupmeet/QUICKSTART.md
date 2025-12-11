# Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Step 1: Start Backend

```bash
cd groupmeet/backend
pip install flask flask-cors
python app.py
```

Backend will run on `http://localhost:5000`

### Step 2: Start Frontend

In a new terminal:

```bash
cd groupmeet/frontend
python -m http.server 3000
```

Frontend will run on `http://localhost:3000`

### Step 3: Test It!

1. Open `http://localhost:3000` in your browser
2. Fill out the form and submit
3. Click "Admin Dashboard" to see submissions
4. Click "Generate Matches" to create groups
5. Check the backend console for simulated email notifications

## 📝 Example Test Data

Submit multiple forms with different courses and availability to test matching:

**Student 1:**
- Course: CIS1200
- Availability: Monday 2-4pm, Wednesday 3-5pm
- Preference: PSets

**Student 2:**
- Course: CIS1200
- Availability: Monday 2-4pm, Friday 10am-12pm
- Preference: PSets

**Student 3:**
- Course: CIS1200
- Availability: Monday 2-4pm, Wednesday 3-5pm
- Preference: Concept Review

These should match into a group!

## 🔧 Troubleshooting

**CORS errors?** Make sure backend is running on port 5000 and frontend on port 3000.

**No matches?** You need at least 3 submissions with overlapping availability.

**Can't see results?** Use the submission ID from the success message and navigate to `/results/<id>`

