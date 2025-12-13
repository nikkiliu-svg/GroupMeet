"""
Custom exceptions for QC module.
"""
from backend.utils.errors import GroupMeetError


class QCError(GroupMeetError):
    """Base exception for QC module."""
    status_code = 400


class EnrollmentVerificationError(QCError):
    """Raised when enrollment verification fails."""
    pass


class DuplicateSubmissionError(QCError):
    """Raised when duplicate submission is detected."""
    pass


class InvalidDataError(QCError):
    """Raised when data validation fails."""
    pass

