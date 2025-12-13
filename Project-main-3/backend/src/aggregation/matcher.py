"""
Match orchestration service.
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging
from backend.models.submission import Submission
from backend.models.match import Match
from backend.src.services.firebase_service import FirebaseService
from backend.src.services.email_service import EmailService
from backend.src.aggregation.clustering import GroupMatcher
from backend.src.aggregation.scoring import CompatibilityScorer

logger = logging.getLogger(__name__)


class InsufficientParticipantsError(Exception):
    """Raised when there are not enough participants to form groups."""
    pass


class MatchOrchestrator:
    """Orchestrates the matching process."""
    
    def __init__(self, firebase_service: FirebaseService, email_service: EmailService, 
                 matcher: GroupMatcher):
        """
        Initialize match orchestrator.
        
        Args:
            firebase_service: Firebase service instance
            email_service: Email service instance
            matcher: Group matcher instance
        """
        self.firebase = firebase_service
        self.email = email_service
        self.matcher = matcher
    
    def run_matching(self, course_id: str, deadline: Optional[datetime] = None) -> Dict:
        """
        Execute matching for a course.
        
        Args:
            course_id: Course identifier
            deadline: Optional deadline (only match submissions before this)
            
        Returns:
            Dictionary with matching results
            
        Raises:
            InsufficientParticipantsError: If not enough participants
        """
        # Fetch all validated submissions for course
        submissions = self.firebase.get_validated_submissions(course_id)
        
        if len(submissions) < self.matcher.min_group_size:
            raise InsufficientParticipantsError(
                f"Need at least {self.matcher.min_group_size} participants, got {len(submissions)}"
            )
        
        logger.info(f"Running matching for {course_id} with {len(submissions)} participants")
        
        # Run matching algorithm
        groups = self.matcher.match_students(submissions, course_id)
        
        if not groups:
            logger.warning(f"No groups formed for {course_id}")
            return {
                'course_id': course_id,
                'matches_created': 0,
                'match_ids': [],
                'timestamp': datetime.utcnow().isoformat(),
                'message': 'No groups could be formed'
            }
        
        # Store matches in Firebase and send emails
        match_ids = []
        feedback_due_date = (datetime.utcnow() + timedelta(days=5)).isoformat()
        
        for group_dict in groups:
            # Create match object
            match = Match.from_dict(group_dict)
            match.feedback_due_date = feedback_due_date
            
            # Store in Firebase
            match_id = self.firebase.create_match(match)
            match_ids.append(match_id)
            
            # Update match_id in the stored match
            match.match_id = match_id
            self.firebase.db.collection('matches').document(match_id).update({
                'match_id': match_id
            })
            
            # Send emails to group members
            try:
                self.email.send_group_intro_email(match.to_dict())
                # Mark feedback as sent
                self.firebase.db.collection('matches').document(match_id).update({
                    'feedback_sent': True
                })
            except Exception as e:
                logger.error(f"Error sending email for match {match_id}: {e}")
        
        logger.info(f"Created {len(match_ids)} matches for {course_id}")
        
        return {
            'course_id': course_id,
            'matches_created': len(match_ids),
            'match_ids': match_ids,
            'timestamp': datetime.utcnow().isoformat()
        }

