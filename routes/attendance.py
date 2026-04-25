"""
Attendance management routes — mark, view, report.
"""
from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.attendance import Attendance
from models.student import Student
from models.course import Course
from models.faculty import Faculty
from routes.auth import faculty_required

attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route('/attendance/mark', methods=['GET', 'POST'])
@login_required
def mark_attendance():
    """Mark attendance for a course on a specific date."""
    if not (current_user.is_admin() or current_user.is_faculty()):
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))

    courses = Course.query.filter_by(college_id=current_user.college_id).order_by(Course.name).all()

    if request.method == 'POST':
        course_id = request.form.get('course_id')
        att_date_str = request.form.get('date', '')

        if not course_id or not att_date_str:
            flash('Please select a course and date.', 'danger')
            return render_template('attendance/mark.html', courses=courses)

        try:
            att_date = datetime.strptime(att_date_str, '%Y-%m-%d').date()
            course = Course.query.filter_by(id=int(course_id), college_id=current_user.college_id).first()
            if not course:
                flash('Course not found.', 'danger')
                return render_template('attendance/mark.html', courses=courses)

            # Get students in this course's department and semester
            students = Student.query.filter_by(
                department=course.department,
                semester=course.semester,
                status='active',
                college_id=current_user.college_id
            ).order_by(Student.name).all()

            # Get faculty for marked_by
            faculty = Faculty.query.filter_by(user_id=current_user.id).first()
            marked_by_id = faculty.id if faculty else None

            # Process attendance for each student
            count_marked = 0
            for student in students:
                status = request.form.get(f'status_{student.id}', '')
                if status in ('present', 'absent', 'late'):
                    # Check if already marked
                    existing = Attendance.query.filter_by(
                        student_id=student.id,
                        course_id=course.id,
                        date=att_date
                    ).first()

                    if existing:
                        existing.status = status
                        existing.marked_by = marked_by_id
                    else:
                        att = Attendance(
                            student_id=student.id,
                            course_id=course.id,
                            date=att_date,
                            status=status,
                            marked_by=marked_by_id
                        )
                        db.session.add(att)
                    count_marked += 1

            db.session.commit()
            flash(f'Attendance marked for {count_marked} students in {course.name}.', 'success')
            return redirect(url_for('attendance.mark_attendance'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error marking attendance: {str(e)}', 'danger')

    # If GET with course_id param, show students for marking
    selected_course_id = request.args.get('course_id', '')
    selected_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    students = []
    existing_attendance = {}

    if selected_course_id:
        course = Course.query.filter_by(id=int(selected_course_id), college_id=current_user.college_id).first()
        if course:
            students = Student.query.filter_by(
                department=course.department,
                semester=course.semester,
                status='active',
                college_id=current_user.college_id
            ).order_by(Student.name).all()

            # Get existing attendance for this date
            att_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
            for att in Attendance.query.filter_by(course_id=course.id, date=att_date).all():
                existing_attendance[att.student_id] = att.status

    return render_template('attendance/mark.html',
                           courses=courses,
                           students=students,
                           selected_course_id=selected_course_id,
                           selected_date=selected_date,
                           existing_attendance=existing_attendance)


@attendance_bp.route('/attendance/view')
@login_required
def view_attendance():
    """View attendance records with filters."""
    course_id = request.args.get('course_id', '')
    student_id = request.args.get('student_id', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    query = db.session.query(Attendance).join(Student).filter(Student.college_id == current_user.college_id)

    if course_id:
        query = query.filter(Attendance.course_id == int(course_id))
    if student_id:
        query = query.filter(Attendance.student_id == int(student_id))
    if date_from:
        query = query.filter(Attendance.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
    if date_to:
        query = query.filter(Attendance.date <= datetime.strptime(date_to, '%Y-%m-%d').date())

    # For student role, filter to only their records
    if current_user.is_student():
        student = Student.query.filter_by(user_id=current_user.id).first()
        if student:
            query = query.filter(Attendance.student_id == student.id)
        else:
            query = query.filter(Attendance.id == -1)

    records = query.order_by(Attendance.date.desc()).limit(500).all()
    courses = Course.query.filter_by(college_id=current_user.college_id).order_by(Course.name).all()
    students = Student.query.filter_by(status='active', college_id=current_user.college_id).order_by(Student.name).all()

    return render_template('attendance/view.html',
                           records=records,
                           courses=courses,
                           students=students,
                           filters={
                               'course_id': course_id,
                               'student_id': student_id,
                               'date_from': date_from,
                               'date_to': date_to
                           })


@attendance_bp.route('/attendance/report')
@login_required
def attendance_report():
    """Attendance report with statistics."""
    courses = Course.query.filter_by(college_id=current_user.college_id).order_by(Course.name).all()
    course_id = request.args.get('course_id', '')

    report_data = []

    if course_id:
        course = Course.query.filter_by(id=int(course_id), college_id=current_user.college_id).first()
        if course:
            students = Student.query.filter_by(
                department=course.department,
                semester=course.semester,
                status='active',
                college_id=current_user.college_id
            ).order_by(Student.name).all()

            for student in students:
                total = Attendance.query.filter_by(student_id=student.id, course_id=course.id).count()
                present = Attendance.query.filter_by(student_id=student.id, course_id=course.id, status='present').count()
                late = Attendance.query.filter_by(student_id=student.id, course_id=course.id, status='late').count()
                absent = Attendance.query.filter_by(student_id=student.id, course_id=course.id, status='absent').count()
                pct = round((present / total * 100), 1) if total > 0 else 0

                report_data.append({
                    'student': student,
                    'total': total,
                    'present': present,
                    'late': late,
                    'absent': absent,
                    'percentage': pct,
                    'at_risk': pct < 75
                })

    return render_template('attendance/report.html',
                           courses=courses,
                           report_data=report_data,
                           selected_course_id=course_id)
