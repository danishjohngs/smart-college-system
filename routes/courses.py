"""
Course CRUD routes — list, add, edit, delete.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.course import Course
from models.faculty import Faculty
from models.student import Student
from routes.auth import admin_required

courses_bp = Blueprint('courses', __name__)


@courses_bp.route('/courses')
@login_required
def list_courses():
    """List all courses with filters."""
    department = request.args.get('department', '')
    semester = request.args.get('semester', '')
    search = request.args.get('search', '')

    query = Course.query.filter_by(college_id=current_user.college_id)

    if department:
        query = query.filter_by(department=department)
    if semester:
        query = query.filter_by(semester=int(semester))
    if search:
        query = query.filter(
            db.or_(
                Course.name.ilike(f'%{search}%'),
                Course.code.ilike(f'%{search}%')
            )
        )

    courses = query.order_by(Course.code).all()
    departments = Student.DEPARTMENTS
    faculty_list = Faculty.query.filter_by(college_id=current_user.college_id).order_by(Faculty.name).all()

    return render_template('courses/list.html',
                           courses=courses,
                           departments=departments,
                           faculty_list=faculty_list,
                           filters={'department': department, 'semester': semester, 'search': search})


@courses_bp.route('/courses/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_course():
    """Add a new course."""
    faculty_list = Faculty.query.filter_by(college_id=current_user.college_id).order_by(Faculty.name).all()

    if request.method == 'POST':
        try:
            course = Course(
                college_id=current_user.college_id,
                code=request.form.get('code', '').strip().upper(),
                name=request.form.get('name', '').strip(),
                department=request.form.get('department', ''),
                semester=int(request.form.get('semester', 1)),
                credits=int(request.form.get('credits', 3)),
                faculty_id=int(request.form.get('faculty_id')) if request.form.get('faculty_id') else None
            )

            if not course.code:
                flash('Course code is required.', 'danger')
                return render_template('courses/add.html', departments=Student.DEPARTMENTS, faculty_list=faculty_list)
            if not course.name:
                flash('Course name is required.', 'danger')
                return render_template('courses/add.html', departments=Student.DEPARTMENTS, faculty_list=faculty_list)
            if Course.query.filter_by(code=course.code).first():
                flash('Course code already exists.', 'danger')
                return render_template('courses/add.html', departments=Student.DEPARTMENTS, faculty_list=faculty_list)

            db.session.add(course)
            db.session.commit()
            flash(f'Course "{course.code}: {course.name}" added successfully.', 'success')
            return redirect(url_for('courses.list_courses'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding course: {str(e)}', 'danger')

    return render_template('courses/add.html', departments=Student.DEPARTMENTS, faculty_list=faculty_list)


@courses_bp.route('/courses/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_course(id):
    """Edit course details."""
    course = Course.query.filter_by(id=id, college_id=current_user.college_id).first_or_404()
    faculty_list = Faculty.query.filter_by(college_id=current_user.college_id).order_by(Faculty.name).all()

    if request.method == 'POST':
        try:
            course.name = request.form.get('name', '').strip()
            course.department = request.form.get('department', '')
            course.semester = int(request.form.get('semester', 1))
            course.credits = int(request.form.get('credits', 3))
            course.faculty_id = int(request.form.get('faculty_id')) if request.form.get('faculty_id') else None

            new_code = request.form.get('code', '').strip().upper()
            if new_code != course.code:
                if Course.query.filter_by(code=new_code).first():
                    flash('Course code already exists.', 'danger')
                    return render_template('courses/edit.html', course=course, departments=Student.DEPARTMENTS, faculty_list=faculty_list)
                course.code = new_code

            db.session.commit()
            flash(f'Course "{course.code}" updated successfully.', 'success')
            return redirect(url_for('courses.list_courses'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating course: {str(e)}', 'danger')

    return render_template('courses/edit.html', course=course, departments=Student.DEPARTMENTS, faculty_list=faculty_list)


@courses_bp.route('/courses/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_course(id):
    """Delete a course."""
    course = Course.query.filter_by(id=id, college_id=current_user.college_id).first_or_404()
    try:
        db.session.delete(course)
        db.session.commit()
        flash(f'Course "{course.code}" deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('courses.list_courses'))
