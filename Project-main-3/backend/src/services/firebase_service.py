"""
Firebase service for data persistence.
"""
import firebase_admin
from firebase_admin import credentials, firestore
from typing import List, Optional, Dict
import logging
from backend.models.submission import Submission
from backend.models.match import Match

logger = logging.getLogger(__name__)


class FirebaseService:
    """Service for interacting with Firebase Firestore."""
    
    def __init__(self, credentials_path: Optional[str] = None, project_id: Optional[str] = None):
        """
        Initialize Firebase service.
        
        Args:
            credentials_path: Path to Firebase service account credentials JSON
            project_id: Firebase project ID
        """
        if not firebase_admin._apps:
            if credentials_path:
                cred = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(cred, {'projectId': project_id})
            elif project_id:
                # Use default credentials (e.g., from environment)
                firebase_admin.initialize_app(project_id=project_id)
            else:
                # Try to use default credentials
                try:
                    firebase_admin.initialize_app()
                except Exception as e:
                    logger.error(f"Failed to initialize Firebase: {e}")
                    raise
        
        self.db = firestore.client()
        logger.info("Firebase service initialized")
    
    # Submission methods
    def create_submission(self, submission: Submission) -> str:
        """Create a new submission."""
        submission_dict = submission.to_dict()
        doc_ref = self.db.collection('submissions').add(submission_dict)
        submission_id = doc_ref[1].id
        logger.info(f"Created submission {submission_id} for user {submission.pennkey}")
        return submission_id
    
    def get_submission(self, submission_id: str) -> Optional[Submission]:
        """Get a submission by ID."""
        doc_ref = self.db.collection('submissions').document(submission_id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return Submission.from_dict(data)
        return None
    
    def get_user_submission(self, pennkey: str, course: str) -> Optional[Submission]:
        """Get a user's submission for a specific course."""
        query = self.db.collection('submissions')\
            .where('pennkey', '==', pennkey)\
            .where('course', '==', course)\
            .limit(1)
        
        docs = query.stream()
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            return Submission.from_dict(data)
        return None
    
    def get_validated_submissions(self, course: str) -> List[Submission]:
        """Get all validated submissions for a course."""
        query = self.db.collection('submissions')\
            .where('course', '==', course)\
            .where('status', '==', 'validated')
        
        submissions = []
        for doc in query.stream():
            data = doc.to_dict()
            data['id'] = doc.id
            submissions.append(Submission.from_dict(data))
        
        return submissions
    
    def update_submission(self, submission_id: str, updates: Dict) -> bool:
        """Update a submission."""
        doc_ref = self.db.collection('submissions').document(submission_id)
        doc_ref.update(updates)
        logger.info(f"Updated submission {submission_id}")
        return True
    
    # Match methods
    def create_match(self, match: Match) -> str:
        """Create a new match."""
        match_dict = match.to_dict()
        doc_ref = self.db.collection('matches').add(match_dict)
        match_id = doc_ref[1].id
        logger.info(f"Created match {match_id} for course {match.course}")
        return match_id
    
    def get_match(self, match_id: str) -> Optional[Match]:
        """Get a match by ID."""
        doc_ref = self.db.collection('matches').document(match_id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            data['match_id'] = doc.id
            return Match.from_dict(data)
        return None
    
    def get_user_match(self, pennkey: str, course: str) -> Optional[Match]:
        """Get a user's match for a specific course."""
        query = self.db.collection('matches')\
            .where('course', '==', course)
        
        docs = query.stream()
        for doc in docs:
            match = Match.from_dict(doc.to_dict())
            match.match_id = doc.id
            # Check if user is in this match
            if any(member.pennkey == pennkey for member in match.members):
                return match
        return None
    
    def get_all_matches(self, course: Optional[str] = None) -> List[Match]:
        """Get all matches, optionally filtered by course."""
        query = self.db.collection('matches')
        if course:
            query = query.where('course', '==', course)
        
        matches = []
        for doc in query.stream():
            data = doc.to_dict()
            data['match_id'] = doc.id
            matches.append(Match.from_dict(data))
        
        return matches
    
    # Roster methods
    def load_roster(self, course_id: str) -> List[str]:
        """Load class roster (list of PennKeys)."""
        doc_ref = self.db.collection('rosters').document(course_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict().get('pennkeys', [])
        return []
    
    def save_roster(self, course_id: str, pennkeys: List[str]) -> bool:
        """Save class roster."""
        doc_ref = self.db.collection('rosters').document(course_id)
        doc_ref.set({'pennkeys': pennkeys})
        logger.info(f"Saved roster for course {course_id} with {len(pennkeys)} students")
        return True
    
    # Feedback methods
    def create_feedback(self, feedback_data: Dict) -> str:
        """Create feedback entry."""
        doc_ref = self.db.collection('feedback').add(feedback_data)
        feedback_id = doc_ref[1].id
        logger.info(f"Created feedback {feedback_id}")
        return feedback_id
    
    def get_feedback(self, match_id: str) -> List[Dict]:
        """Get all feedback for a match."""
        query = self.db.collection('feedback')\
            .where('match_id', '==', match_id)
        
        feedback_list = []
        for doc in query.stream():
            data = doc.to_dict()
            data['id'] = doc.id
            feedback_list.append(data)
        
        return feedback_list

