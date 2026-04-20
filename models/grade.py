"""
Grade model for managing academic grades and CGPA.
"""
from extensions import db


class Grade(db.Model):
    """Grade model for storing student academic performance."""
    __tablename__ = 'grades'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    internal_marks = db.Column(db.Float, default=0.0)
    external_marks = db.Column(db.Float, default=0.0)
    total_marks = db.Column(db.Float, default=0.0)
    grade = db.Column(db.String(5))  # A+, A, B+, B, C+, C, D, F
    grade_point = db.Column(db.Float, default=0.0)

    # Unique constraint: one grade per student per course
    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', name='unique_student_course_grade'),
    )

    # Grade mapping based on total marks
    GRADE_SCALE = [
        (90, 100, 'A+', 10.0),
        (80, 89, 'A', 9.0),
        (70, 79, 'B+', 8.0),
        (60, 69, 'B', 7.0),
        (50, 59, 'C+', 6.0),
        (40, 49, 'C', 5.0),
        (30, 39, 'D', 4.0),
        (0, 29, 'F', 0.0),
    ]

    def calculate_grade(self):
        """Auto-calculate total marks, letter grade, and grade point."""
        self.total_marks = (self.internal_marks or 0) + (self.external_marks or 0)
        for low, high, letter, point in self.GRADE_SCALE:
            if low <= self.total_marks <= high:
                self.grade = letter
                self.grade_point = point
                return
        # Fallback for out-of-range
        self.grade = 'F'
        self.grade_point = 0.0

    def __repr__(self):
        return f'<Grade Student:{self.student_id} Course:{self.course_id} {self.grade}>'
