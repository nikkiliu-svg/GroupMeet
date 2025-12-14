"""
Authentication routes for CAS SSO integration.
"""
from flask import Blueprint, redirect, request, session, url_for, jsonify, current_app
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login endpoint - CAS in production, dev form in development mode."""
    dev_mode = current_app.config.get('DEV_BYPASS_AUTH', False)
    
    # Development mode: show login form
    if dev_mode:
        if request.method == 'POST':
            # Handle dev login form submission
            data = request.get_json() if request.is_json else request.form
            username = data.get('username', '').strip()
            
            if not username:
                return jsonify({'error': 'Username is required'}), 400
            
            # Create session with provided username
            session['pennkey'] = username
            session['authenticated'] = True
            session['attributes'] = {'name': username.title()}  # Capitalize for display
            
            logger.info(f"Development mode: User logged in as {username}")
            
            if request.is_json:
                return jsonify({
                    'status': 'ok',
                    'message': 'Logged in successfully',
                    'pennkey': username
                }), 200
            else:
                return redirect('http://localhost:3000/dashboard')
        else:
            # GET request - redirect to frontend (frontend will show dev login form)
            return redirect('http://localhost:3000/?dev_mode=true')
    
    # Production mode: redirect to CAS
    cas_client = getattr(current_app, "cas_client", None)

    if cas_client is None:
        logger.error("CAS client not initialized")
        return jsonify({'error': 'Authentication service not configured'}), 500
    
    # Get callback URL - build from request
    callback_path = url_for('auth.callback', _external=False)
    
    # Always use localhost:5000 for callback (backend URL)
    callback_url = f"http://localhost:5000{callback_path}"
    
    logger.info(f"Production mode: Redirecting to CAS with callback URL: {callback_url}")

    # Build CAS login URL
    cas_login_url = cas_client.get_login_url(callback_url)
    logger.info(f"CAS login URL: {cas_login_url}")

    return redirect(cas_login_url)


@auth_bp.route('/callback')
def callback():
    """Handle CAS callback after authentication."""
    cas_client = getattr(current_app, "cas_client", None)

    if cas_client is None:
        logger.error("CAS client not initialized in callback")
        return jsonify({'error': 'Authentication service not configured'}), 500

    ticket = request.args.get('ticket')
    
    if not ticket:
        logger.warning("CAS callback called without ticket")
        return jsonify({'error': 'No ticket provided'}), 400

    try:
        # Get service URL (callback URL without ticket)
        # Always use localhost:5000 for service URL
        service_url = f"http://localhost:5000{url_for('auth.callback', _external=False)}"
        
        logger.info(f"Validating ticket with service URL: {service_url}")

        # Validate ticket with CAS
        pennkey, attributes = cas_client.validate_ticket(ticket, service_url)

        # Store in session
        session['pennkey'] = pennkey
        session['authenticated'] = True
        session['attributes'] = attributes

        logger.info(f"User authenticated: {pennkey}")

        # Redirect to frontend dashboard
        frontend_url = "http://localhost:3000"
        return redirect(f"{frontend_url}/dashboard")

    except Exception as e:
        logger.error(f"CAS callback error: {e}")
        return jsonify({'error': f'Authentication failed: {str(e)}'}), 401


@auth_bp.route('/logout')
def logout():
    """Logout and clear session."""
    cas_client = getattr(current_app, "cas_client", None)

    pennkey = session.get('pennkey', 'unknown')
    session.clear()
    
    logger.info(f"User logged out: {pennkey}")

    if cas_client is None:
        return redirect('http://localhost:3000')

    # Build service URL from request
    login_path = url_for('auth.login', _external=False)
    service_url = f"http://localhost:5000{login_path}"
    
    cas_logout_url = cas_client.get_logout_url(service_url)
    return redirect(cas_logout_url)


@auth_bp.route('/status')
def status():
    """Check authentication status."""
    is_authenticated = session.get('authenticated', False)
    dev_mode = current_app.config.get('DEV_BYPASS_AUTH', False)

    if is_authenticated:
        return jsonify({
            'authenticated': True,
            'pennkey': session.get('pennkey'),
            'attributes': session.get('attributes', {}),
            'dev_mode': dev_mode
        }), 200

    return jsonify({
        'authenticated': False,
        'dev_mode': dev_mode
    }), 200

