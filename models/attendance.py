"""
Attendance model for tracking student attendance.
"""
from extensions import db


class Attendance(db.Model):
    """Attendance model for tracking daily student attendance per course."""
    __tablename__ = 'attendances'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(10), nullable=False, default='present')  # present, absent, late
    marked_by = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=True)

    # Unique constraint: one attendance per student per course per date
    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', 'date', name='unique_attendance'),
    )

    def __repr__(self):
        return f'<Attendance Student:{self.student_id} Course:{self.course_id} {self.date} {self.status}>'
