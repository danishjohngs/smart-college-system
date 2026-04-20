"""
Smart College Management System with AI-Based Predictive Analytics
Main Flask Application Entry Point

Authors: Adhithyan, Jaymon, Joel, Joy
St Benedict Academy — BCA Final Year Project, 2026
"""
import os
from flask import Flask, redirect, url_for
from config import Config
from extensions import db, login_manager


def create_app():
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # User loader for Flask-Login
    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.students import students_bp
    from routes.faculty import faculty_bp
    from routes.courses import courses_bp
    from routes.attendance import attendance_bp
    from routes.grades import grades_bp
    from routes.predictions import predictions_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(faculty_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(grades_bp)
    app.register_blueprint(predictions_bp)
    app.register_blueprint(api_bp)

    # Root route
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return """
        <!DOCTYPE html>
        <html>
        <head><title>404 — Page Not Found</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            body { font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
            .container { text-align: center; }
            h1 { font-size: 6rem; color: #3b82f6; margin: 0; }
            p { font-size: 1.2rem; margin: 1rem 0; }
            a { color: #3b82f6; text-decoration: none; font-weight: 600; }
            a:hover { text-decoration: underline; }
        </style>
        </head>
        <body>
            <div class="container">
                <h1>404</h1>
                <p><i class="fas fa-exclamation-triangle"></i> Page Not Found</p>
                <a href="/dashboard"><i class="fas fa-arrow-left"></i> Return to Dashboard</a>
            </div>
        </body>
        </html>
        """, 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return """
        <!DOCTYPE html>
        <html>
        <head><title>500 — Server Error</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
            .container { text-align: center; }
            h1 { font-size: 6rem; color: #ef4444; margin: 0; }
            p { font-size: 1.2rem; margin: 1rem 0; }
            a { color: #3b82f6; text-decoration: none; font-weight: 600; }
        </style>
        </head>
        <body>
            <div class="container">
                <h1>500</h1>
                <p>Internal Server Error</p>
                <a href="/dashboard">Return to Dashboard</a>
            </div>
        </body>
        </html>
        """, 500

    # Create database tables
    with app.app_context():
        db.create_all()
        # Create saved_models directory if it doesn't exist
        os.makedirs(os.path.join(app.root_path, 'ml', 'saved_models'), exist_ok=True)

    return app


# Module-level app instance (required by Vercel)
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
