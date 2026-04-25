"""
User model for authentication and authorization.
Supports roles: admin, faculty, student.
Includes approval workflow for self-registration.
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class User(UserMixin, db.Model):
    """User model for authentication."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # admin, faculty, student
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    college_id = db.Column(db.Integer, db.ForeignKey('colleges.id'), nullable=True)
    college = db.relationship('College', foreign_keys=[college_id], backref='users')

    # --- Approval Workflow Fields ---
    status = db.Column(db.String(20), nullable=False, default='pending')
    # Values: 'pending', 'approved', 'rejected'

    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    # Which admin approved/rejected this user

    approved_at = db.Column(db.DateTime, nullable=True)
    # When was the approval action taken

    rejection_reason = db.Column(db.Text, nullable=True)
    # If rejected, why

    full_name = db.Column(db.String(100), nullable=True)
    # Full name of the person registering

    department = db.Column(db.String(50), nullable=True)
    # Department the user belongs to (for verification)

    id_proof_number = db.Column(db.String(50), nullable=True)
    # College ID / Admission number / Employee ID for verification

    phone = db.Column(db.String(15), nullable=True)
    # Contact number

    # --- Role-Specific Fields ---
    gender = db.Column(db.String(10), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    profile_photo = db.Column(db.String(200), nullable=True)
    address = db.Column(db.Text, nullable=True)

    # Admin fields
    college_name = db.Column(db.String(200), nullable=True)
    college_location = db.Column(db.String(200), nullable=True)
    admin_designation = db.Column(db.String(100), nullable=True)

    # Faculty fields
    designation = db.Column(db.String(100), nullable=True)
    qualification = db.Column(db.String(100), nullable=True)
    specialization = db.Column(db.String(100), nullable=True)
    years_of_experience = db.Column(db.Integer, nullable=True)
    date_of_joining = db.Column(db.Date, nullable=True)

    # Student fields
    semester = db.Column(db.Integer, nullable=True)
    admission_year = db.Column(db.Integer, nullable=True)
    graduation_year = db.Column(db.Integer, nullable=True)
    programme = db.Column(db.String(100), nullable=True)
    blood_group = db.Column(db.String(5), nullable=True)
    parent_name = db.Column(db.String(100), nullable=True)
    parent_phone = db.Column(db.String(15), nullable=True)

    # Relationships
    student = db.relationship('Student', backref='user', uselist=False, lazy=True)
    faculty = db.relationship('Faculty', backref='user', uselist=False, lazy=True)

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify the user's password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_faculty(self):
        return self.role == 'faculty'

    def is_student(self):
        return self.role == 'student'

    def is_approved(self):
        return self.status == 'approved'

    def is_pending(self):
        return self.status == 'pending'

    def is_rejected(self):
        return self.status == 'rejected'

    def __repr__(self):
        return f'<User {self.username} ({self.role}) [{self.status}]>'
