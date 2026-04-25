"""
Configuration settings for the Smart College Management System.
Supports environment variables for production deployment.
"""
import os


class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'smart-college-secret-key-2026'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///college.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Vercel: use /tmp for instance folder (read-only filesystem)
    if os.environ.get('VERCEL'):
        SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/college.db'

    # First-time setup key — change this before deployment
    SETUP_KEY = os.environ.get('SETUP_KEY') or 'COLLEGE-SETUP-2026'

    # =====================================================
    # Email Configuration — Gmail SMTP (WORKING)
    # =====================================================
    MAIL_ENABLED = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'smartcollegeai@gmail.com'
    MAIL_PASSWORD = 'fpkquaupbeizionk'
    MAIL_DEFAULT_SENDER = 'smartcollegeai@gmail.com'
    MAIL_SENDER_NAME = 'Smart College Management System'
    MAIL_SENDER_EMAIL = 'smartcollegeai@gmail.com'