"""
Submission data model.
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional


@dataclass
class Submission:
    """Represents a student submission/preference form."""
    
    id: Optional[str] = None
    pennkey: str = ''
    course: str = ''
    availability: List[str] = None
    study_style: str = ''  # visual, textual, auditory, kinesthetic
    goal: str = ''  # problem_sets, concept_review, exam_prep
    preferred_group_size: int = 4
    status: str = 'pending'  # pending, validated, matched
    created_at: Optional[str] = None
    validated_at: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.availability is None:
            self.availability = []
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for Firebase storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Submission':
        """Create Submission from dictionary."""
        return cls(**data)
    
    def validate(self) -> List[str]:
        """
        Validate submission data.
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        if not self.pennkey:
            errors.append('PennKey is required')
        
        if not self.course:
            errors.append('Course is required')
        
        if not self.availability or len(self.availability) == 0:
            errors.append('At least one availability slot is required')
        
        valid_study_styles = ['visual', 'textual', 'auditory', 'kinesthetic']
        if self.study_style and self.study_style not in valid_study_styles:
            errors.append(f'Invalid study style. Must be one of: {", ".join(valid_study_styles)}')
        
        valid_goals = ['problem_sets', 'concept_review', 'exam_prep']
        if self.goal and self.goal not in valid_goals:
            errors.append(f'Invalid goal. Must be one of: {", ".join(valid_goals)}')
        
        if self.preferred_group_size < 2 or self.preferred_group_size > 6:
            errors.append('Preferred group size must be between 2 and 6')
        
        return errors

