"""
Custom exceptions for aggregation module.
"""
from backend.utils.errors import GroupMeetError


class AggregationError(GroupMeetError):
    """Base exception for aggregation module."""
    status_code = 500


class InsufficientParticipantsError(AggregationError):
    """Raised when there are not enough participants to form groups."""
    pass

