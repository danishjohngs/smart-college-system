"""
Models package for the Smart College Management System.
Imports all models so they can be accessed from models package directly.
"""
from models.user import User
from models.student import Student
from models.faculty import Faculty
from models.course import Course
from models.attendance import Attendance
from models.grade import Grade
from models.admission import AdmissionRecord
from models.prediction import Prediction

__all__ = [
    'User', 'Student', 'Faculty', 'Course',
    'Attendance', 'Grade', 'AdmissionRecord', 'Prediction'
]
