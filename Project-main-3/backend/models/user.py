"""
User profile data model.
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """Represents a user profile."""
    
    pennkey: str
    email: str
    name: Optional[str] = None
    is_admin: bool = False
    created_at: Optional[str] = None
    last_login: Optional[str] = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for Firebase storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create User from dictionary."""
        return cls(**data)

