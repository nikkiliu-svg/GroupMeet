"""
Authentication middleware for protecting routes.
"""
from functools import wraps
from flask import session, jsonify
from backend.utils.errors import AuthenticationError, AuthorizationError
import logging

logger = logging.getLogger(__name__)


def require_auth(f):
    """
    Decorator to require authentication.
    
    Usage:
        @require_auth
        def my_protected_route():
            pennkey = session['pennkey']
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'authenticated' not in session or not session.get('authenticated'):
            logger.warning("Unauthorized access attempt")
            raise AuthenticationError("Authentication required")
        return f(*args, **kwargs)
    return decorated_function


def require_admin(f):
    """
    Decorator to require admin privileges.
    
    Usage:
        @require_admin
        def my_admin_route():
            ...
    """
    @wraps(f)
    @require_auth
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin', False):
            logger.warning(f"Admin access denied for user: {session.get('pennkey')}")
            raise AuthorizationError("Admin access required")
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """
    Get current authenticated user's pennkey.
    
    Returns:
        str: Current user's pennkey
        
    Raises:
        AuthenticationError: If user is not authenticated
    """
    if 'authenticated' not in session or not session.get('authenticated'):
        raise AuthenticationError("Not authenticated")
    return session.get('pennkey')

