"""
Configuration management for GroupMeet backend.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class."""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # CAS Configuration
    CAS_SERVER_ROOT = os.environ.get('CAS_SERVER_ROOT') or \
        'https://alliance.seas.upenn.edu/~lumbroso/cgi-bin/cas/'
    
    # Firebase Configuration
    FIREBASE_API_KEY = os.environ.get('FIREBASE_API_KEY')
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID')
    FIREBASE_STORAGE_BUCKET = os.environ.get('FIREBASE_STORAGE_BUCKET')
    FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH')
    
    # SendGrid Configuration
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@groupmeet.upenn.edu')
    
    # Application Configuration
    ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
    DEBUG = ENVIRONMENT == 'development'
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Matching Configuration
    MIN_GROUP_SIZE = int(os.environ.get('MIN_GROUP_SIZE', '3'))
    MAX_GROUP_SIZE = int(os.environ.get('MAX_GROUP_SIZE', '5'))
    FEEDBACK_REMINDER_DAYS = int(os.environ.get('FEEDBACK_REMINDER_DAYS', '5'))


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    ENVIRONMENT = 'development'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    ENVIRONMENT = 'production'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

