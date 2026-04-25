"""
Faculty model for managing faculty records.
"""
from extensions import db


class Faculty(db.Model):
    """Faculty model with professional information."""
    __tablename__ = 'faculty'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    college_id = db.Column(db.Integer, db.ForeignKey('colleges.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(15))
    department = db.Column(db.String(50), nullable=False)
    designation = db.Column(db.String(50))
    qualification = db.Column(db.String(100))

    status = db.Column(db.String(20), default='active')
    # Values: 'active', 'removed'

    removed_at = db.Column(db.DateTime, nullable=True)
    removed_reason = db.Column(db.Text, nullable=True)

    # Relationships
    courses = db.relationship('Course', backref='faculty', lazy=True)
    marked_attendances = db.relationship('Attendance', backref='marker', lazy=True,
                                          foreign_keys='Attendance.marked_by')

    def is_removed(self):
        """Check if this faculty has been archived/removed."""
        return self.status == 'removed'

    def __repr__(self):
        return f'<Faculty {self.name} ({self.employee_id})>'

