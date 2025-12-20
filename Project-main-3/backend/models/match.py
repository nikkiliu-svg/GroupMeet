"""
Match/Group data model.
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional
from backend.models.submission import Submission


@dataclass
class Member:
    """Represents a member in a study group."""
    pennkey: str
    email: str
    name: Optional[str] = None


@dataclass
class Match:
    """Represents a matched study group."""
    
    match_id: Optional[str] = None
    group_id: int = 0
    course: str = ''
    members: List[Member] = None
    compatibility_score: float = 0.0
    suggested_meeting_time: str = ''
    created_at: Optional[str] = None
    feedback_sent: bool = False
    feedback_due_date: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.members is None:
            self.members = []
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for Firebase storage."""
        data = asdict(self)
        # Convert Member objects to dicts
        data['members'] = [asdict(member) if isinstance(member, Member) else member 
                          for member in data['members']]
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Match':
        """Create Match from dictionary."""
        # Convert member dicts to Member objects
        if 'members' in data and data['members']:
            data['members'] = [Member(**m) if isinstance(m, dict) else m 
                              for m in data['members']]
        return cls(**data)

