"""
Authentication middleware for protecting routes.
"""
from functools import wraps
from flask import session, jsonify, redirect, url_for, request
import logging

logger = logging.getLogger(__name__)


def require_auth(f):
    """
    Decorator to require authentication for a route.
    Redirects to login if not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'authenticated' not in session or not session.get('authenticated'):
            # If it's an API request, return JSON error
            if request.path.startswith('/api/') or request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            # Otherwise redirect to login
            return redirect('/auth/login')
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Get current authenticated user's PennKey from session."""
    if session.get('authenticated'):
        return session.get('pennkey')
    return None

