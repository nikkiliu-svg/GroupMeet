"""
Authentication routes for CAS SSO integration.
"""
from flask import Blueprint, redirect, request, session, url_for, jsonify
from urllib.parse import quote
from backend.auth.cas_client import cas_client
from backend.utils.errors import AuthenticationError
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login')
def login():
    """
    Redirect to CAS login page.
    """
    if cas_client is None:
        logger.error("CAS client not initialized")
        return jsonify({'error': 'Authentication service not configured'}), 500
    
    # Get the callback URL for this request
    callback_url = url_for('auth.callback', _external=True)
    
    # Redirect to CAS login
    cas_login_url = cas_client.get_login_url(callback_url)
    logger.info(f"Redirecting to CAS login: {cas_login_url}")
    return redirect(cas_login_url)


@auth_bp.route('/callback')
def callback():
    """
    Handle CAS callback after authentication.
    """
    ticket = request.args.get('ticket')
    
    if not ticket:
        logger.warning("CAS callback called without ticket")
        return jsonify({'error': 'No ticket provided'}), 400
    
    try:
        # Get the service URL (the callback URL without the ticket parameter)
        service_url = request.url.split('?')[0]
        
        # Validate ticket with CAS server
        pennkey, attributes = cas_client.validate_ticket(ticket, service_url)
        
        # Store in session
        session['pennkey'] = pennkey
        session['authenticated'] = True
        session['attributes'] = attributes
        
        # Check if admin (could be based on attributes or separate admin list)
        # For now, we'll implement a simple admin check
        session['is_admin'] = False  # TODO: Implement admin check based on attributes
        
        logger.info(f"User authenticated: {pennkey}")
        
        # Redirect to frontend (frontend will handle routing)
        # In production, this should redirect to the frontend URL
        frontend_url = request.host_url.rstrip('/').replace(':5000', ':3000')  # Dev assumption
        return redirect(f"{frontend_url}/dashboard")
        
    except Exception as e:
        logger.error(f"CAS callback error: {e}")
        return jsonify({'error': f'Authentication failed: {str(e)}'}), 401


@auth_bp.route('/logout')
def logout():
    """
    Logout and clear session, then redirect to CAS logout.
    """
    pennkey = session.get('pennkey', 'unknown')
    
    # Clear session
    session.clear()
    
    logger.info(f"User logged out: {pennkey}")
    
    # Redirect to CAS logout
    if cas_client is None:
        return jsonify({'message': 'Logged out'}), 200
    
    # Optionally redirect back to app after logout
    service_url = url_for('auth.login', _external=True)
    cas_logout_url = cas_client.get_logout_url(service_url)
    return redirect(cas_logout_url)


@auth_bp.route('/status')
def status():
    """
    Check current authentication status.
    """
    is_authenticated = session.get('authenticated', False)
    
    if is_authenticated:
        return jsonify({
            'authenticated': True,
            'pennkey': session.get('pennkey'),
            'is_admin': session.get('is_admin', False)
        }), 200
    else:
        return jsonify({
            'authenticated': False
        }), 200

