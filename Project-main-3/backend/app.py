"""
GroupMeet Flask application factory.
"""
from flask import Flask
from flask_cors import CORS
from backend.config import config
from backend.utils.logging_config import setup_logging
from backend.utils.errors import GroupMeetError, handle_error
from backend.auth.routes import auth_bp
from backend.auth.cas_client import init_cas_client
from backend.src.services.firebase_service import FirebaseService

# Initialize logging
logger = setup_logging()


def create_app(config_name='default'):
    """
    Create and configure Flask application.
    
    Args:
        config_name: Configuration name ('development', 'production', or 'default')
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize CORS
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    
    # Initialize CAS client
    init_cas_client(app.config['CAS_SERVER_ROOT'])
    logger.info(f"CAS client initialized with server: {app.config['CAS_SERVER_ROOT']}")
    
    # Initialize Firebase service
    try:
        firebase_service = FirebaseService(
            credentials_path=app.config.get('FIREBASE_CREDENTIALS_PATH'),
            project_id=app.config.get('FIREBASE_PROJECT_ID')
        )
        # Store in app context for access in routes
        app.firebase_service = firebase_service
        logger.info("Firebase service initialized")
    except Exception as e:
        logger.warning(f"Firebase initialization failed: {e}. Some features may not work.")
        app.firebase_service = None
    
    # Register error handlers
    app.register_error_handler(GroupMeetError, handle_error)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    
    # Register API blueprints
    from backend.api.submissions import submissions_bp
    from backend.api.matches import matches_bp
    from backend.api.feedback import feedback_bp
    from backend.api.admin import admin_bp
    
    app.register_blueprint(submissions_bp)
    app.register_blueprint(matches_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(admin_bp)
    
    # Health check endpoint
    @app.route('/health')
    def health():
        """Health check endpoint."""
        return {'status': 'ok', 'environment': app.config['ENVIRONMENT']}, 200
    
    logger.info(f"Flask app created in {app.config['ENVIRONMENT']} mode")
    return app


if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)

