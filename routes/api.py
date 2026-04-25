"""
API routes — JSON endpoints for Chart.js dashboards.
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from extensions import db
from models.student import Student
from models.faculty import Faculty
from models.course import Course
from models.attendance import Attendance
from models.grade import Grade
from models.admission import AdmissionRecord
from models.prediction import Prediction

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/dashboard-stats')
@login_required
def dashboard_stats():
    """Return dashboard summary statistics as JSON."""
    total_students = Student.query.filter_by(status='active', college_id=current_user.college_id).count()
    total_faculty = Faculty.query.filter(Faculty.status != 'removed', Faculty.college_id == current_user.college_id).count()
    total_courses = Course.query.filter_by(college_id=current_user.college_id).count()

    # Department counts
    departments = Student.DEPARTMENTS
    dept_data = {}
    for dept in departments:
        dept_data[dept] = Student.query.filter_by(department=dept, status='active', college_id=current_user.college_id).count()

    # Total attendance
    total_attendance = Attendance.query.count()
    present_count = Attendance.query.filter_by(status='present').count()
    attendance_rate = round((present_count / total_attendance * 100), 1) if total_attendance > 0 else 0

    # At-risk count
    at_risk = Prediction.query.filter_by(prediction_type='performance', predicted_value=0, college_id=current_user.college_id).count()

    return jsonify({
        'total_students': total_students,
        'total_faculty': total_faculty,
        'total_courses': total_courses,
        'department_data': dept_data,
        'attendance_rate': attendance_rate,
        'at_risk_count': at_risk
    })


@api_bp.route('/api/attendance-chart/<int:student_id>')
@login_required
def attendance_chart(student_id):
    """Return attendance data for a specific student."""
    student = Student.query.filter_by(id=student_id, college_id=current_user.college_id).first_or_404()
    courses = Course.query.filter_by(
        department=student.department,
        semester=student.semester
    ).all()

    chart_data = {'labels': [], 'present': [], 'absent': [], 'late': []}

    for course in courses:
        chart_data['labels'].append(course.code)
        total = Attendance.query.filter_by(student_id=student_id, course_id=course.id).count()
        present = Attendance.query.filter_by(student_id=student_id, course_id=course.id, status='present').count()
        absent = Attendance.query.filter_by(student_id=student_id, course_id=course.id, status='absent').count()
        late = Attendance.query.filter_by(student_id=student_id, course_id=course.id, status='late').count()
        chart_data['present'].append(present)
        chart_data['absent'].append(absent)
        chart_data['late'].append(late)

    return jsonify(chart_data)


@api_bp.route('/api/grade-distribution')
@login_required
def grade_distribution():
    """Return grade distribution data."""
    department = request.args.get('department', '')
    grade_counts = {'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C+': 0, 'C': 0, 'D': 0, 'F': 0}

    query = db.session.query(Grade).join(Student).filter(Student.college_id == current_user.college_id)
    if department:
        student_ids = [s.id for s in Student.query.filter_by(department=department, college_id=current_user.college_id).all()]
        query = query.filter(Grade.student_id.in_(student_ids))

    for grade in query.all():
        if grade.grade in grade_counts:
            grade_counts[grade.grade] += 1

    return jsonify({
        'labels': list(grade_counts.keys()),
        'data': list(grade_counts.values())
    })


@api_bp.route('/api/admission-trends')
@login_required
def admission_trends():
    """Return admission trend data for charts."""
    department = request.args.get('department', '')

    query = AdmissionRecord.query.filter_by(college_id=current_user.college_id).order_by(AdmissionRecord.year)
    if department:
        query = query.filter_by(department=department)

    records = query.all()

    # Group by year
    years = sorted(set(r.year for r in records))
    data = {
        'labels': years,
        'applications': [],
        'admitted': [],
        'capacity': []
    }

    for year in years:
        year_records = [r for r in records if r.year == year]
        data['applications'].append(sum(r.applications_received for r in year_records))
        data['admitted'].append(sum(r.students_admitted for r in year_records))
        data['capacity'].append(sum(r.total_capacity for r in year_records))

    return jsonify(data)


@api_bp.route('/api/department-stats')
@login_required
def department_stats():
    """Return department-wise statistics."""
    departments = Student.DEPARTMENTS
    data = []

    for dept in departments:
        students = Student.query.filter_by(department=dept, status='active', college_id=current_user.college_id).all()
        avg_cgpa = sum(s.cgpa for s in students) / len(students) if students else 0

        # Average attendance
        total_att = 0
        present_att = 0
        for s in students:
            student_att = Attendance.query.filter_by(student_id=s.id).all()
            total_att += len(student_att)
            present_att += sum(1 for a in student_att if a.status == 'present')

        att_pct = round((present_att / total_att * 100), 1) if total_att > 0 else 0

        data.append({
            'department': dept,
            'student_count': len(students),
            'avg_cgpa': round(avg_cgpa, 2),
            'attendance_pct': att_pct
        })

    return jsonify(data)
