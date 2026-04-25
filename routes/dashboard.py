"""
Dashboard routes — role-based dashboards for admin, faculty, and students.
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models.student import Student
from models.faculty import Faculty
from models.course import Course
from models.attendance import Attendance
from models.grade import Grade
from models.prediction import Prediction
from models.college import College

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Redirect to role-specific dashboard."""
    if current_user.is_admin():
        return redirect(url_for('dashboard.admin_dashboard'))
    elif current_user.is_faculty():
        return redirect(url_for('dashboard.faculty_dashboard'))
    else:
        return redirect(url_for('dashboard.student_dashboard'))


@dashboard_bp.route('/dashboard/admin')
@login_required
def admin_dashboard():
    """Admin dashboard with overview statistics."""
    if not current_user.is_admin():
        return redirect(url_for('dashboard.index'))

    college = College.query.get(current_user.college_id) if current_user.college_id else None

    total_students = Student.query.filter_by(status='active', college_id=current_user.college_id).count()
    total_faculty = Faculty.query.filter(Faculty.status != 'removed', Faculty.college_id == current_user.college_id).count()
    total_courses = Course.query.filter_by(college_id=current_user.college_id).count()

    # Department-wise student count
    departments = ['Computer Science', 'Electronics', 'Mechanical', 'Electrical', 'Civil']
    dept_counts = {}
    for dept in departments:
        dept_counts[dept] = Student.query.filter_by(department=dept, status='active', college_id=current_user.college_id).count()

    # At-risk students (predicted performance category = 0)
    # Using a join or filtering predictions where student is in this college.
    # A simple way: join Student
    at_risk_count = db.session.query(Prediction).join(Student).filter(
        Prediction.prediction_type == 'performance',
        Prediction.predicted_value == 0,
        Student.college_id == current_user.college_id
    ).count()

    # Recent predictions
    recent_predictions = db.session.query(Prediction).join(Student).filter(
        Student.college_id == current_user.college_id
    ).order_by(Prediction.created_at.desc()).limit(5).all()

    # Attendance stats
    total_attendance = db.session.query(Attendance).join(Student).filter(Student.college_id == current_user.college_id).count()
    present_count = db.session.query(Attendance).join(Student).filter(Student.college_id == current_user.college_id, Attendance.status == 'present').count()
    attendance_rate = round((present_count / total_attendance * 100), 1) if total_attendance > 0 else 0

    return render_template('dashboard/admin_dashboard.html',
                           college=college,
                           total_students=total_students,
                           total_faculty=total_faculty,
                           total_courses=total_courses,
                           dept_counts=dept_counts,
                           at_risk_count=at_risk_count,
                           recent_predictions=recent_predictions,
                           attendance_rate=attendance_rate)


@dashboard_bp.route('/dashboard/faculty')
@login_required
def faculty_dashboard():
    """Faculty dashboard with their courses and students."""
    if not (current_user.is_faculty() or current_user.is_admin()):
        return redirect(url_for('dashboard.index'))

    college = College.query.get(current_user.college_id) if current_user.college_id else None
    faculty = Faculty.query.filter_by(user_id=current_user.id).first()
    courses = []
    my_students_count = 0

    if faculty:
        courses = Course.query.filter_by(faculty_id=faculty.id).all()
        # Count active students in the faculty's department
        my_students_count = Student.query.filter_by(
            status='active',
            department=faculty.department,
            college_id=current_user.college_id
        ).count()

    total_students = Student.query.filter_by(status='active', college_id=current_user.college_id).count()
    total_courses = Course.query.filter_by(college_id=current_user.college_id).count()

    return render_template('dashboard/faculty_dashboard.html',
                           college=college,
                           faculty=faculty,
                           courses=courses,
                           my_students_count=my_students_count,
                           total_students=total_students,
                           total_courses=total_courses)


@dashboard_bp.route('/dashboard/student')
@login_required
def student_dashboard():
    """Student dashboard with their academic info."""
    if not (current_user.is_student() or current_user.is_admin()):
        return redirect(url_for('dashboard.index'))

    college = College.query.get(current_user.college_id) if current_user.college_id else None
    student = Student.query.filter_by(user_id=current_user.id).first()
    attendance_pct = 0
    grades = []
    predictions_list = []

    if student:
        attendance_pct = student.get_attendance_percentage()
        grades = Grade.query.filter_by(student_id=student.id).all()
        predictions_list = Prediction.query.filter_by(
            student_id=student.id, prediction_type='performance'
        ).order_by(Prediction.created_at.desc()).limit(5).all()

    return render_template('dashboard/student_dashboard.html',
                           college=college,
                           student=student,
                           attendance_pct=attendance_pct,
                           grades=grades,
                           predictions=predictions_list)
