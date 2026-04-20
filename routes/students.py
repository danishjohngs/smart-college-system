"""
Student CRUD routes — list, add, edit, profile, delete.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.student import Student
from models.user import User
from models.grade import Grade
from models.attendance import Attendance
from models.prediction import Prediction
from routes.auth import admin_required, faculty_required

students_bp = Blueprint('students', __name__)


@students_bp.route('/students')
@login_required
def list_students():
    """List all students with search and filter."""
    department = request.args.get('department', '')
    semester = request.args.get('semester', '')
    status = request.args.get('status', '')
    search = request.args.get('search', '')

    query = Student.query

    if department:
        query = query.filter_by(department=department)
    if semester:
        query = query.filter_by(semester=int(semester))
    if status:
        query = query.filter_by(status=status)
    if search:
        query = query.filter(
            db.or_(
                Student.name.ilike(f'%{search}%'),
                Student.roll_number.ilike(f'%{search}%'),
                Student.email.ilike(f'%{search}%')
            )
        )

    students = query.order_by(Student.name).all()
    departments = Student.DEPARTMENTS

    return render_template('students/list.html',
                           students=students,
                           departments=departments,
                           filters={
                               'department': department,
                               'semester': semester,
                               'status': status,
                               'search': search
                           })


@students_bp.route('/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    """Add a new student."""
    if not (current_user.is_admin() or current_user.is_faculty()):
        flash('Access denied.', 'danger')
        return redirect(url_for('students.list_students'))

    if request.method == 'POST':
        try:
            student = Student(
                name=request.form.get('name', '').strip(),
                roll_number=request.form.get('roll_number', '').strip(),
                email=request.form.get('email', '').strip(),
                phone=request.form.get('phone', '').strip(),
                department=request.form.get('department', ''),
                semester=int(request.form.get('semester', 1)),
                admission_year=int(request.form.get('admission_year', 2024)),
                gender=request.form.get('gender', ''),
                address=request.form.get('address', '').strip(),
                status='active'
            )

            dob = request.form.get('date_of_birth', '')
            if dob:
                from datetime import datetime
                student.date_of_birth = datetime.strptime(dob, '%Y-%m-%d').date()

            # Validation
            if not student.name:
                flash('Student name is required.', 'danger')
                return render_template('students/add.html', departments=Student.DEPARTMENTS)
            if not student.roll_number:
                flash('Roll number is required.', 'danger')
                return render_template('students/add.html', departments=Student.DEPARTMENTS)
            if Student.query.filter_by(roll_number=student.roll_number).first():
                flash('Roll number already exists.', 'danger')
                return render_template('students/add.html', departments=Student.DEPARTMENTS)

            db.session.add(student)
            db.session.commit()
            flash(f'Student "{student.name}" added successfully.', 'success')
            return redirect(url_for('students.list_students'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding student: {str(e)}', 'danger')

    return render_template('students/add.html', departments=Student.DEPARTMENTS)


@students_bp.route('/students/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    """Edit student details."""
    if not (current_user.is_admin() or current_user.is_faculty()):
        flash('Access denied.', 'danger')
        return redirect(url_for('students.list_students'))

    student = Student.query.get_or_404(id)

    if request.method == 'POST':
        try:
            student.name = request.form.get('name', '').strip()
            student.email = request.form.get('email', '').strip()
            student.phone = request.form.get('phone', '').strip()
            student.department = request.form.get('department', '')
            student.semester = int(request.form.get('semester', 1))
            student.gender = request.form.get('gender', '')
            student.address = request.form.get('address', '').strip()
            student.status = request.form.get('status', 'active')

            dob = request.form.get('date_of_birth', '')
            if dob:
                from datetime import datetime
                student.date_of_birth = datetime.strptime(dob, '%Y-%m-%d').date()

            new_roll = request.form.get('roll_number', '').strip()
            if new_roll != student.roll_number:
                if Student.query.filter_by(roll_number=new_roll).first():
                    flash('Roll number already exists.', 'danger')
                    return render_template('students/edit.html', student=student, departments=Student.DEPARTMENTS)
                student.roll_number = new_roll

            db.session.commit()
            flash(f'Student "{student.name}" updated successfully.', 'success')
            return redirect(url_for('students.profile', id=student.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating student: {str(e)}', 'danger')

    return render_template('students/edit.html', student=student, departments=Student.DEPARTMENTS)


@students_bp.route('/students/profile/<int:id>')
@login_required
def profile(id):
    """View student profile with academic details."""
    student = Student.query.get_or_404(id)

    # Check student access — students can only see their own profile
    if current_user.is_student():
        own_student = Student.query.filter_by(user_id=current_user.id).first()
        if not own_student or own_student.id != id:
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard.index'))

    attendance_pct = student.get_attendance_percentage()
    grades = Grade.query.filter_by(student_id=student.id).all()
    predictions_list = Prediction.query.filter_by(
        student_id=student.id, prediction_type='performance'
    ).order_by(Prediction.created_at.desc()).limit(5).all()

    # Calculate per-course attendance
    course_attendance = {}
    for att in student.attendances:
        course = att.course
        if course.id not in course_attendance:
            course_attendance[course.id] = {
                'course': course,
                'total': 0,
                'present': 0
            }
        course_attendance[course.id]['total'] += 1
        if att.status == 'present':
            course_attendance[course.id]['present'] += 1

    for cid in course_attendance:
        total = course_attendance[cid]['total']
        present = course_attendance[cid]['present']
        course_attendance[cid]['percentage'] = round((present / total * 100), 1) if total > 0 else 0

    return render_template('students/profile.html',
                           student=student,
                           attendance_pct=attendance_pct,
                           grades=grades,
                           predictions=predictions_list,
                           course_attendance=course_attendance)


@students_bp.route('/students/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_student(id):
    """Delete (deactivate) a student."""
    student = Student.query.get_or_404(id)
    try:
        student.status = 'inactive'
        db.session.commit()
        flash(f'Student "{student.name}" has been deactivated.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('students.list_students'))
