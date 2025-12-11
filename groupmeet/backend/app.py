"""
Flask application for GroupMeet MVP.
"""
from flask import Flask, request, jsonify, session
from flask import send_from_directory
from flask_cors import CORS
import logging
import uuid
import os

from config import Config
from db import get_database
from matching import match_students
from qc.quality_control import validate_submission, sanitize_submission
from aggregation.aggregate import aggregate_feedback
from emailer import get_email_transporter, send_match_notification
from auth.routes import auth_bp
from auth.cas_client import init_cas_client
from auth.middleware import require_auth, get_current_user

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['DEV_BYPASS_AUTH'] = Config.DEV_BYPASS_AUTH

# Enable CORS with credentials for session cookies
CORS(app, origins=["*"], supports_credentials=True)

# Initialize CAS client
init_cas_client(app, Config.CAS_SERVER_ROOT)

# Register auth blueprint
app.register_blueprint(auth_bp)

# Initialize database
db = get_database(Config)

# Initialize email transporter
email_transporter = get_email_transporter(Config)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "message": "GroupMeet API is running"}), 200


@app.route('/api/submit', methods=['POST'])
@require_auth
def submit():
    """
    Submit a new student form (requires authentication).
    
    Expected JSON:
    {
        "course": "CIS1200",
        "availability": ["Monday 2-4pm", "Wednesday 3-5pm"],
        "study_preference": "PSets",
        "location_preference": "In-person",
        "commitment_confirmed": true
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Get authenticated user
        pennkey = get_current_user()
        if not pennkey:
            return jsonify({"error": "Not authenticated"}), 401
        
        # Check if student already has a submission for this course
        existing_submissions = db.get_all_submissions()
        for sub in existing_submissions:
            if sub.get('pennkey') == pennkey and sub.get('course') == data.get('course'):
                return jsonify({
                    "error": f"You already have a submission for {data.get('course')}"
                }), 400
        
        # Build submission data with auth info
        # Handle email: if pennkey already contains @, use it as-is (normalized); otherwise append @upenn.edu
        if '@' in pennkey:
            email = pennkey.lower().strip()  # User entered an email-like username, normalize it
        else:
            email = f"{pennkey}@upenn.edu"  # Default email format
        
        submission_data = {
            'pennkey': pennkey,
            'name': session.get('attributes', {}).get('name', pennkey),  # Use CAS attributes if available
            'email': email,
            'course': data.get('course'),
            'availability': data.get('availability', []),
            'study_preference': data.get('study_preference'),
            'location_preference': data.get('location_preference', 'Either'),
            'commitment_confirmed': data.get('commitment_confirmed', False)
        }
        
        # Sanitize input
        sanitized = sanitize_submission(submission_data)
        
        # Validate submission
        validation = validate_submission(sanitized)
        
        if not validation["valid"]:
            return jsonify({
                "error": "Validation failed",
                "errors": validation["errors"]
            }), 400
        
        # Generate submission ID
        submission_id = str(uuid.uuid4())
        sanitized['id'] = submission_id
        
        # Save to database
        saved_id = db.save_submission(sanitized)
        
        logger.info(f"Submission saved: {saved_id} for {pennkey} in {sanitized.get('course')}")
        
        # Automatic matching: Check if we should run matching for this course
        course = sanitized.get('course')
        course_submissions = [s for s in db.get_all_submissions() if s.get('course') == course]
        
        if len(course_submissions) >= Config.MIN_GROUP_SIZE:
            logger.info(f"Auto-matching triggered for {course} ({len(course_submissions)} students)")
            try:
                matched_groups, unmatched = match_students(
                    course_submissions,
                    min_group_size=Config.MIN_GROUP_SIZE,
                    max_group_size=Config.MAX_GROUP_SIZE
                )
                
                # Save matches and send notifications
                for group in matched_groups:
                    match_id = db.save_match(group)
                    
                    for student in group['group_members']:
                        student_id = student['id']
                        match_url = f"{Config.BASE_URL}/dashboard"
                        
                        # Get student email from submission
                        student_sub = db.get_submission(student_id)
                        if student_sub:
                            student_email = student_sub.get('email', f"{student_sub.get('pennkey', 'student')}@upenn.edu")
                        else:
                            student_email = student.get('email', 'student@upenn.edu')
                        
                        send_match_notification(
                            email_transporter,
                            student_email,
                            student['name'],
                            match_url,
                            group['group_members'],
                            Config
                        )
                    
                    logger.info(f"Created match {match_id} for {course}")
                
                logger.info(f"Auto-matching complete: {len(matched_groups)} groups created")
            except Exception as e:
                logger.error(f"Error in auto-matching: {e}")
                # Don't fail the submission if matching fails
        
        return jsonify({
            "status": "ok",
            "id": saved_id,
            "message": "Submission saved successfully"
        }), 201
    
    except Exception as e:
        logger.error(f"Error in /api/submit: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/submissions', methods=['GET'])
def get_submissions():
    """
    Get all submissions (admin-only in production).
    For MVP, no authentication required.
    """
    try:
        submissions = db.get_all_submissions()
        
        # Remove sensitive data if needed (for MVP, return all)
        return jsonify({
            "status": "ok",
            "count": len(submissions),
            "submissions": submissions
        }), 200
    
    except Exception as e:
        logger.error(f"Error in /submissions: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/match', methods=['POST'])
def match():
    """
    Run the matching algorithm and generate groups.
    
    Optional JSON:
    {
        "course": "CIS1200"  # Optional: match only for specific course
    }
    """
    try:
        data = request.get_json() or {}
        course_filter = data.get('course')
        
        # Get all submissions
        all_submissions = db.get_all_submissions()
        
        if not all_submissions:
            return jsonify({
                "error": "No submissions found"
            }), 400
        
        # Filter by course if specified
        if course_filter:
            submissions = [s for s in all_submissions if s.get('course') == course_filter]
        else:
            submissions = all_submissions
        
        if len(submissions) < Config.MIN_GROUP_SIZE:
            return jsonify({
                "error": f"Not enough submissions (need at least {Config.MIN_GROUP_SIZE})"
            }), 400
        
        # Run matching algorithm
        matched_groups, unmatched = match_students(
            submissions,
            min_group_size=Config.MIN_GROUP_SIZE,
            max_group_size=Config.MAX_GROUP_SIZE
        )
        
        # Save matches to database and generate URLs
        match_results = []
        for group in matched_groups:
            # Save match
            match_id = db.save_match(group)
            
            # Generate match URLs for each student
            for student in group['group_members']:
                student_id = student['id']
                match_url = f"{Config.BASE_URL}/results/{student_id}"
                
                # Send notification (simulated email)
                send_match_notification(
                    email_transporter,
                    student['email'],
                    student['name'],
                    match_url,
                    group['group_members'],
                    Config
                )
            
            match_results.append({
                "match_id": match_id,
                "course": group['course'],
                "group_size": group['group_size'],
                "student_count": len(group['student_ids'])
            })
        
        logger.info(f"Generated {len(matched_groups)} matches, {len(unmatched)} unmatched")
        
        return jsonify({
            "status": "ok",
            "matches_created": len(matched_groups),
            "unmatched_count": len(unmatched),
            "matches": match_results,
            "unmatched_students": [
                {
                    "id": s.get('id'),
                    "name": s.get('name'),
                    "email": s.get('email')
                }
                for s in unmatched
            ]
        }), 200
    
    except Exception as e:
        logger.error(f"Error in /match: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/my-groups', methods=['GET'])
@require_auth
def get_my_groups():
    """Get all groups for the current authenticated user."""
    try:
        pennkey = get_current_user()
        if not pennkey:
            return jsonify({"error": "Not authenticated"}), 401
        
        # Get all submissions for this user
        all_submissions = db.get_all_submissions()
        user_submissions = [s for s in all_submissions if s.get('pennkey') == pennkey]
        
        # Get all matches for this user
        groups = []
        for submission in user_submissions:
            submission_id = submission.get('id')
            matches = db.get_matches_by_student(submission_id)
            
            for match in matches:
                # Find user's group members (exclude self)
                group_members = [
                    member for member in match.get('group_members', [])
                    if member.get('id') != submission_id
                ]
                
                groups.append({
                    "match_id": match.get('id'),
                    "course": match.get('course'),
                    "group_members": group_members,
                    "group_size": match.get('group_size', 0),
                    "availability_overlap": match.get('availability_overlap', 0.0),
                    "preference_alignment": match.get('preference_alignment', 0.0),
                    "avg_compatibility": match.get('avg_compatibility', 0.0),
                    "submission_id": submission_id
                })
        
        return jsonify({
            "status": "ok",
            "groups": groups,
            "count": len(groups)
        }), 200
    
    except Exception as e:
        logger.error(f"Error in /api/my-groups: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/my-submissions', methods=['GET'])
@require_auth
def get_my_submissions():
    """Get all submissions for the current authenticated user."""
    try:
        pennkey = get_current_user()
        if not pennkey:
            return jsonify({"error": "Not authenticated"}), 401
        
        # Get all submissions for this user
        all_submissions = db.get_all_submissions()
        user_submissions = [s for s in all_submissions if s.get('pennkey') == pennkey]
        
        return jsonify({
            "status": "ok",
            "submissions": user_submissions,
            "count": len(user_submissions)
        }), 200
    
    except Exception as e:
        logger.error(f"Error in /api/my-submissions: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/group/<match_id>', methods=['GET'])
@require_auth
def get_group_details(match_id):
    """Get detailed information about a specific group."""
    try:
        pennkey = get_current_user()
        if not pennkey:
            return jsonify({"error": "Not authenticated"}), 401
        
        # Get the match
        match = db.get_match(match_id)
        if not match:
            return jsonify({"error": "Group not found"}), 404
        
        # Verify user is in this group
        user_submissions = [s for s in db.get_all_submissions() if s.get('pennkey') == pennkey]
        user_submission_ids = {s.get('id') for s in user_submissions}
        
        if not any(sid in match.get('student_ids', []) for sid in user_submission_ids):
            return jsonify({"error": "You are not a member of this group"}), 403
        
        # Get full group information
        group_members = match.get('group_members', [])
        
        return jsonify({
            "status": "ok",
            "match": {
                "id": match.get('id'),
                "course": match.get('course'),
                "group_members": group_members,
                "group_size": match.get('group_size', 0),
                "availability_overlap": match.get('availability_overlap', 0.0),
                "preference_alignment": match.get('preference_alignment', 0.0),
                "avg_compatibility": match.get('avg_compatibility', 0.0)
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error in /api/group/{match_id}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/results/<student_id>', methods=['GET'])
def get_results(student_id):
    """
    Get match results for a specific student (legacy endpoint, kept for compatibility).
    
    Args:
        student_id: Student submission ID
    """
    try:
        # Get student submission
        student = db.get_submission(student_id)
        
        if not student:
            return jsonify({"error": "Student not found"}), 404
        
        # Find matches for this student
        matches = db.get_matches_by_student(student_id)
        
        if not matches:
            return jsonify({
                "student": {
                    "id": student.get('id'),
                    "name": student.get('name'),
                    "email": student.get('email')
                },
                "message": "No matches found yet"
            }), 200
        
        # Get the most recent match (or first if multiple)
        match = matches[0]
        
        # Find student's group members (exclude self)
        group_members = [
            member for member in match.get('group_members', [])
            if member.get('id') != student_id
        ]
        
        return jsonify({
            "student": {
                "id": student.get('id'),
                "name": student.get('name'),
                "email": student.get('email'),
                "course": student.get('course'),
                "study_preference": student.get('study_preference')
            },
            "group_members": group_members,
            "availability_overlap": match.get('availability_overlap', 0.0),
            "preference_alignment": match.get('preference_alignment', 0.0),
            "avg_compatibility": match.get('avg_compatibility', 0.0),
            "match_id": match.get('id')
        }), 200
    
    except Exception as e:
        logger.error(f"Error in /results/{student_id}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/feedback', methods=['POST'])
def submit_feedback():
    """
    Submit feedback for a match.
    
    Expected JSON:
    {
        "match_id": "uuid",
        "student_id": "uuid",
        "rating": 5,  # 1-5 stars
        "comments": "Great group!"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        required_fields = ['match_id', 'student_id', 'rating']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        rating = data.get('rating')
        if not isinstance(rating, int) or not (1 <= rating <= 5):
            return jsonify({"error": "Rating must be an integer between 1 and 5"}), 400
        
        # In a full implementation, save feedback to database
        # For MVP, we'll just return success
        logger.info(f"Feedback submitted: match_id={data.get('match_id')}, rating={rating}")
        
        return jsonify({
            "status": "ok",
            "message": "Feedback submitted successfully"
        }), 200
    
    except Exception as e:
        logger.error(f"Error in /feedback: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/feedback/aggregate', methods=['POST'])
def aggregate_feedback_endpoint():
    """
    Aggregate feedback ratings.
    
    Expected JSON:
    {
        "feedback_list": [
            {"rating": 5, "comments": "..."},
            {"rating": 4, "comments": "..."}
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'feedback_list' not in data:
            return jsonify({"error": "No feedback_list provided"}), 400
        
        feedback_list = data['feedback_list']
        result = aggregate_feedback(feedback_list)
        
        return jsonify({
            "status": "ok",
            "aggregation": result
        }), 200
    
    except Exception as e:
        logger.error(f"Error in /feedback/aggregate: {e}")
        return jsonify({"error": str(e)}), 500

# Serve frontend static files in production
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve frontend files."""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    if path != "" and os.path.exists(os.path.join(frontend_path, path)):
        return send_from_directory(frontend_path, path)
    else:
        return send_from_directory(frontend_path, "index.html")


if __name__ == '__main__':
    logger.info("Starting GroupMeet backend server...")
    logger.info(f"Database type: {Config.DB_TYPE}")
    logger.info(f"Email provider: {Config.EMAIL_PROVIDER}")
    
    # Log authentication mode
    if Config.DEV_BYPASS_AUTH:
        logger.info("=" * 60)
        logger.info("🔧 DEVELOPMENT MODE: CAS authentication BYPASSED")
        logger.info("   Users can login with username/email (no password)")
        logger.info("   Set DEV_BYPASS_AUTH=false for production (PennKey/CAS)")
        logger.info("=" * 60)
    else:
        logger.info("=" * 60)
        logger.info("🔐 PRODUCTION MODE: Using PennKey/CAS authentication")
        logger.info("   Set DEV_BYPASS_AUTH=true for development mode")
        logger.info("=" * 60)
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )

