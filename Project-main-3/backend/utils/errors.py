"""
Custom error handlers for the GroupMeet API.
"""
from flask import jsonify
from functools import wraps


class GroupMeetError(Exception):
    """Base exception for GroupMeet application."""
    status_code = 500
    
    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        return rv


class ValidationError(GroupMeetError):
    """Raised when validation fails."""
    status_code = 400


class AuthenticationError(GroupMeetError):
    """Raised when authentication fails."""
    status_code = 401


class AuthorizationError(GroupMeetError):
    """Raised when authorization fails."""
    status_code = 403


class NotFoundError(GroupMeetError):
    """Raised when resource not found."""
    status_code = 404


def handle_error(error):
    """Error handler for GroupMeet errors."""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

