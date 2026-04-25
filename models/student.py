"""
Student model for managing student records.
"""
from extensions import db


class Student(db.Model):
    """Student model with academic and personal information."""
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    college_id = db.Column(db.Integer, db.ForeignKey('colleges.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(15))
    department = db.Column(db.String(50), nullable=False)
    semester = db.Column(db.Integer, nullable=False, default=1)
    admission_year = db.Column(db.Integer)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    address = db.Column(db.Text)
    cgpa = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='active')
    # Values: 'active', 'inactive', 'graduated', 'removed'

    removed_at = db.Column(db.DateTime, nullable=True)
    removed_reason = db.Column(db.Text, nullable=True)

    # Relationships
    attendances = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')
    grades = db.relationship('Grade', backref='student', lazy=True, cascade='all, delete-orphan')
    predictions = db.relationship('Prediction', backref='student', lazy=True, cascade='all, delete-orphan')

    # Valid departments
    DEPARTMENTS = [
        'Computer Science', 'Electronics', 'Mechanical', 'Electrical', 'Civil'
    ]

    def get_attendance_percentage(self, course_id=None):
        """Calculate attendance percentage for a specific course or overall."""
        if course_id:
            records = [a for a in self.attendances if a.course_id == course_id]
        else:
            records = self.attendances
        if not records:
            return 0.0
        present = sum(1 for a in records if a.status == 'present')
        return round((present / len(records)) * 100, 2)

    def is_removed(self):
        """Check if this student has been archived/removed."""
        return self.status == 'removed'

    def __repr__(self):
        return f'<Student {self.name} ({self.roll_number})>'
