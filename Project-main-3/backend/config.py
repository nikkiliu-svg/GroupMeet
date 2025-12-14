"""
Configuration management for GroupMeet backend.
"""
import os
from typing import Dict, Any

class Config:
    """Base configuration class."""
    
    # Database Configuration
    DB_TYPE = os.environ.get('DB_TYPE', 'memory')  # 'memory', 'firestore', or 'sheets'
    
    # Firebase/Firestore Configuration
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID', '')
    FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH', '')
    
    # Google Sheets Configuration
    GOOGLE_SHEETS_ID = os.environ.get('GOOGLE_SHEETS_ID', '')
    GOOGLE_CREDENTIALS_PATH = os.environ.get('GOOGLE_CREDENTIALS_PATH', '')
    
    # Email Configuration (for future use)
    EMAIL_PROVIDER = os.environ.get('EMAIL_PROVIDER', 'console')  # 'console', 'sendgrid', 'smtp'
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', '')
    FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@groupmeet.local')
    
    # Matching Configuration
    MIN_GROUP_SIZE = int(os.environ.get('MIN_GROUP_SIZE', '3'))
    MAX_GROUP_SIZE = int(os.environ.get('MAX_GROUP_SIZE', '5'))
    AVAILABILITY_WEIGHT = float(os.environ.get('AVAILABILITY_WEIGHT', '0.7'))
    PREFERENCE_WEIGHT = float(os.environ.get('PREFERENCE_WEIGHT', '0.3'))
    
    # Application Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', '5000'))
    
    # Base URL for match links
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:3000')
    
    # CAS Authentication Configuration
    CAS_SERVER_ROOT = os.environ.get('CAS_SERVER_ROOT') or \
        'https://alliance.seas.upenn.edu/~lumbroso/cgi-bin/cas/'
    
    # Development mode: bypass CAS authentication (for local testing)
    # Set DEV_BYPASS_AUTH=true to enable
    DEV_BYPASS_AUTH = os.environ.get('DEV_BYPASS_AUTH', 'False').lower() == 'true'

