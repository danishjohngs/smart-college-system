"""
Course model for managing academic courses.
"""
from extensions import db


class Course(db.Model):
    """Course model with academic details."""
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    college_id = db.Column(db.Integer, db.ForeignKey('colleges.id'), nullable=True)
    code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    credits = db.Column(db.Integer, nullable=False, default=3)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=True)

    # Relationships
    attendances = db.relationship('Attendance', backref='course', lazy=True, cascade='all, delete-orphan')
    grades = db.relationship('Grade', backref='course', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Course {self.code}: {self.name}>'
