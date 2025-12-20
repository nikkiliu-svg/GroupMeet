"""
Service for managing class rosters and enrollment verification.
"""
from typing import List, Optional
import logging
from backend.src.services.firebase_service import FirebaseService

logger = logging.getLogger(__name__)


class RosterService:
    """Service for managing class rosters."""
    
    def __init__(self, firebase_service: FirebaseService):
        """
        Initialize roster service.
        
        Args:
            firebase_service: Firebase service instance
        """
        self.firebase = firebase_service
    
    def load_roster(self, course_id: str) -> List[str]:
        """
        Load class roster from Firebase.
        
        Args:
            course_id: Course identifier (e.g., 'CIS1200')
            
        Returns:
            List of PennKeys enrolled in the course
        """
        try:
            pennkeys = self.firebase.load_roster(course_id)
            logger.info(f"Loaded roster for {course_id}: {len(pennkeys)} students")
            return pennkeys
        except Exception as e:
            logger.error(f"Error loading roster for {course_id}: {e}")
            return []
    
    def save_roster(self, course_id: str, pennkeys: List[str]) -> bool:
        """
        Save class roster to Firebase.
        
        Args:
            course_id: Course identifier
            pennkeys: List of PennKeys to save
            
        Returns:
            True if successful
        """
        try:
            return self.firebase.save_roster(course_id, pennkeys)
        except Exception as e:
            logger.error(f"Error saving roster for {course_id}: {e}")
            return False
    
    def is_enrolled(self, pennkey: str, course_id: str) -> bool:
        """
        Check if a PennKey is enrolled in a course.
        
        Args:
            pennkey: Student's PennKey
            course_id: Course identifier
            
        Returns:
            True if enrolled, False otherwise
        """
        roster = self.load_roster(course_id)
        is_enrolled = pennkey.lower() in [pk.lower() for pk in roster]
        
        if not is_enrolled:
            logger.warning(f"PennKey {pennkey} not found in roster for {course_id}")
        
        return is_enrolled
    
    def import_roster_from_list(self, course_id: str, pennkeys: List[str]) -> bool:
        """
        Import roster from a list of PennKeys.
        
        Args:
            course_id: Course identifier
            pennkeys: List of PennKeys
            
        Returns:
            True if successful
        """
        # Normalize PennKeys (lowercase)
        normalized_pennkeys = [pk.lower().strip() for pk in pennkeys if pk.strip()]
        return self.save_roster(course_id, normalized_pennkeys)

