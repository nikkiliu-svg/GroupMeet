"""
Submission validators for QC module.
"""
from typing import List, Optional
from dataclasses import dataclass
import logging
from backend.models.submission import Submission
from backend.src.qc.roster_service import RosterService
from backend.src.services.firebase_service import FirebaseService
from backend.src.qc.exceptions import (
    EnrollmentVerificationError,
    DuplicateSubmissionError,
    InvalidDataError
)

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of submission validation."""
    is_valid: bool
    errors: List[str]
    sanitized_data: Optional[dict] = None


class SubmissionValidator:
    """Validator for student submissions."""
    
    def __init__(self, roster_service: RosterService, firebase_service: FirebaseService):
        """
        Initialize validator.
        
        Args:
            roster_service: Service for roster operations
            firebase_service: Service for Firebase operations
        """
        self.roster_service = roster_service
        self.firebase = firebase_service
    
    def validate_submission(self, submission_data: dict, pennkey: str) -> ValidationResult:
        """
        Validate a submission.
        
        Args:
            submission_data: Submission data from request
            pennkey: Authenticated user's PennKey
            
        Returns:
            ValidationResult with validation status and errors
        """
        errors = []
        
        # Create submission object for validation
        submission_data['pennkey'] = pennkey
        submission = Submission.from_dict(submission_data)
        
        # Run built-in validation
        validation_errors = submission.validate()
        if validation_errors:
            errors.extend(validation_errors)
        
        # Check enrollment
        if submission.course:
            if not self.roster_service.is_enrolled(pennkey, submission.course):
                errors.append(f'Not enrolled in course {submission.course}')
        
        # Check for duplicate submission
        existing_submission = self.firebase.get_user_submission(pennkey, submission.course)
        if existing_submission:
            errors.append(f'Already submitted for course {submission.course}')
        
        # Sanitize availability slots (normalize format)
        if submission.availability:
            submission.availability = self._sanitize_availability(submission.availability)
        
        # Normalize course code (uppercase, remove spaces)
        if submission.course:
            submission.course = submission.course.upper().strip()
        
        if errors:
            return ValidationResult(
                is_valid=False,
                errors=errors,
                sanitized_data=None
            )
        
        # Return sanitized data
        sanitized = submission.to_dict()
        sanitized['status'] = 'pending'  # Will be set to 'validated' after QC
        
        return ValidationResult(
            is_valid=True,
            errors=[],
            sanitized_data=sanitized
        )
    
    def _sanitize_availability(self, availability: List[str]) -> List[str]:
        """
        Sanitize and normalize availability slots.
        
        Args:
            availability: List of availability strings
            
        Returns:
            Sanitized list of availability strings
        """
        valid_slots = []
        valid_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        valid_times = ['AM', 'PM']
        
        for slot in availability:
            if not slot or not isinstance(slot, str):
                continue
            
            # Normalize format: Day_Time (e.g., "Mon_PM")
            parts = slot.strip().split('_')
            if len(parts) == 2:
                day, time = parts
                day = day.capitalize()
                time = time.upper()
                
                if day in valid_days and time in valid_times:
                    valid_slots.append(f"{day}_{time}")
        
        return list(set(valid_slots))  # Remove duplicates

