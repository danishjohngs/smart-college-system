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