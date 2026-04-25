"""
History routes — view archived/removed student and faculty records.
Admin-only, read-only access to historical academic data.
"""
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from models.student import Student
from models.faculty import Faculty
from models.attendance import Attendance
from models.grade import Grade
from models.prediction import Prediction
from models.course import Course
from routes.auth import admin_required

history_bp = Blueprint('history', __name__)


@history_bp.route('/history')
@login_required
@admin_required
def index():
    """History dashboard — overview of all archived records."""
    removed_students = Student.query.filter_by(status='removed').order_by(Student.name).all()
    removed_faculty = Faculty.query.filter_by(status='removed').order_by(Faculty.name).all()

    total_removed_students = len(removed_students)
    total_removed_faculty = len(removed_faculty)

    # Total archived attendance & grade records (from removed students)
    removed_student_ids = [s.id for s in removed_students]
    archived_attendance_count = Attendance.query.filter(
        Attendance.student_id.in_(removed_student_ids)
    ).count() if removed_student_ids else 0

    archived_grade_count = Grade.query.filter(
        Grade.student_id.in_(removed_student_ids)
    ).count() if removed_student_ids else 0

    return render_template('history/index.html',
                           removed_students=removed_students,
                           removed_faculty=removed_faculty,
                           total_removed_students=total_removed_students,
                           total_removed_faculty=total_removed_faculty,
                           archived_attendance_count=archived_attendance_count,
                           archived_grade_count=archived_grade_count)


@history_bp.route('/history/student/<int:id>')
@login_required
@admin_required
def student_history(id):
    """View complete archived records for a removed student."""
    student = Student.query.get_or_404(id)

    if student.status != 'removed':
        flash('This student is still active. View their profile from the Students page.', 'info')
        return redirect(url_for('students.profile', id=id))

    # Get all their historical data
    attendance_records = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.date.desc()).all()
    grade_records = Grade.query.filter_by(student_id=student.id).all()
    prediction_records = Prediction.query.filter_by(student_id=student.id).order_by(Prediction.created_at.desc()).all()

    # Calculate historical attendance percentage
    total_attendance = len(attendance_records)
    present_count = sum(1 for a in attendance_records if a.status == 'present')
    attendance_pct = round((present_count / total_attendance * 100), 1) if total_attendance > 0 else 0

    # Group grades by semester
    semester_grades = {}
    for grade in grade_records:
        sem = grade.semester
        if sem not in semester_grades:
            semester_grades[sem] = []
        semester_grades[sem].append(grade)

    # Course-wise attendance
    course_attendance = {}
    for att in attendance_records:
        cid = att.course_id
        if cid not in course_attendance:
            course = Course.query.get(cid)
            course_attendance[cid] = {
                'course': course,
                'total': 0, 'present': 0, 'absent': 0, 'late': 0
            }
        course_attendance[cid]['total'] += 1
        if att.status == 'present':
            course_attendance[cid]['present'] += 1
        elif att.status == 'absent':
            course_attendance[cid]['absent'] += 1
        elif att.status == 'late':
            course_attendance[cid]['late'] += 1

    for cid in course_attendance:
        total = course_attendance[cid]['total']
        present = course_attendance[cid]['present']
        course_attendance[cid]['percentage'] = round((present / total * 100), 1) if total > 0 else 0

    return render_template('history/student_detail.html',
                           student=student,
                           attendance_records=attendance_records,
                           grade_records=grade_records,
                           prediction_records=prediction_records,
                           attendance_pct=attendance_pct,
                           semester_grades=semester_grades,
                           course_attendance=course_attendance,
                           total_attendance=total_attendance)


@history_bp.route('/history/faculty/<int:id>')
@login_required
@admin_required
def faculty_history(id):
    """View archived records for a removed faculty member."""
    faculty = Faculty.query.get_or_404(id)

    if faculty.status != 'removed':
        flash('This faculty is still active.', 'info')
        return redirect(url_for('faculty.list_faculty'))

    # Get courses they previously taught
    courses = Course.query.filter_by(faculty_id=faculty.id).all()

    # Get attendance records they marked
    marked_attendance = Attendance.query.filter_by(marked_by=faculty.id).count()

    return render_template('history/faculty_detail.html',
                           faculty=faculty,
                           courses=courses,
                           marked_attendance=marked_attendance)
