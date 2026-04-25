"""
Faculty CRUD routes — list, add, edit, delete.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.faculty import Faculty
from models.student import Student
from routes.auth import admin_required

faculty_bp = Blueprint('faculty', __name__)


@faculty_bp.route('/faculty')
@login_required
def list_faculty():
    """List all faculty members with search/filter."""
    department = request.args.get('department', '')
    search = request.args.get('search', '')

    query = Faculty.query.filter(Faculty.status != 'removed', Faculty.college_id == current_user.college_id)

    if department:
        query = query.filter_by(department=department)
    if search:
        query = query.filter(
            db.or_(
                Faculty.name.ilike(f'%{search}%'),
                Faculty.employee_id.ilike(f'%{search}%'),
                Faculty.email.ilike(f'%{search}%')
            )
        )

    faculty_list = query.order_by(Faculty.name).all()
    departments = Student.DEPARTMENTS

    return render_template('faculty/list.html',
                           faculty_list=faculty_list,
                           departments=departments,
                           filters={'department': department, 'search': search})


@faculty_bp.route('/faculty/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_faculty():
    """Add a new faculty member."""
    if request.method == 'POST':
        try:
            fac = Faculty(
                college_id=current_user.college_id,
                name=request.form.get('name', '').strip(),
                employee_id=request.form.get('employee_id', '').strip(),
                email=request.form.get('email', '').strip(),
                phone=request.form.get('phone', '').strip(),
                department=request.form.get('department', ''),
                designation=request.form.get('designation', '').strip(),
                qualification=request.form.get('qualification', '').strip()
            )

            if not fac.name:
                flash('Faculty name is required.', 'danger')
                return render_template('faculty/add.html', departments=Student.DEPARTMENTS)
            if not fac.employee_id:
                flash('Employee ID is required.', 'danger')
                return render_template('faculty/add.html', departments=Student.DEPARTMENTS)
            if Faculty.query.filter_by(employee_id=fac.employee_id).first():
                flash('Employee ID already exists.', 'danger')
                return render_template('faculty/add.html', departments=Student.DEPARTMENTS)

            db.session.add(fac)
            db.session.commit()
            flash(f'Faculty "{fac.name}" added successfully.', 'success')
            return redirect(url_for('faculty.list_faculty'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding faculty: {str(e)}', 'danger')

    return render_template('faculty/add.html', departments=Student.DEPARTMENTS)


@faculty_bp.route('/faculty/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_faculty(id):
    """Edit faculty details."""
    fac = Faculty.query.filter_by(id=id, college_id=current_user.college_id).first_or_404()

    if request.method == 'POST':
        try:
            fac.name = request.form.get('name', '').strip()
            fac.email = request.form.get('email', '').strip()
            fac.phone = request.form.get('phone', '').strip()
            fac.department = request.form.get('department', '')
            fac.designation = request.form.get('designation', '').strip()
            fac.qualification = request.form.get('qualification', '').strip()

            new_eid = request.form.get('employee_id', '').strip()
            if new_eid != fac.employee_id:
                if Faculty.query.filter_by(employee_id=new_eid).first():
                    flash('Employee ID already exists.', 'danger')
                    return render_template('faculty/edit.html', faculty=fac, departments=Student.DEPARTMENTS)
                fac.employee_id = new_eid

            db.session.commit()
            flash(f'Faculty "{fac.name}" updated successfully.', 'success')
            return redirect(url_for('faculty.list_faculty'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating faculty: {str(e)}', 'danger')

    return render_template('faculty/edit.html', faculty=fac, departments=Student.DEPARTMENTS)


@faculty_bp.route('/faculty/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_faculty(id):
    """Archive a faculty member — mark as removed, delete user account."""
    fac = Faculty.query.filter_by(id=id, college_id=current_user.college_id).first_or_404()
    faculty_name = fac.name
    user_id = fac.user_id

    try:
        from datetime import datetime

        # 1. Mark faculty as 'removed'
        fac.status = 'removed'
        fac.removed_at = datetime.utcnow()
        fac.user_id = None  # Unlink from user account

        # 2. Unlink courses (set faculty_id to NULL — don't delete courses)
        from models.course import Course
        Course.query.filter_by(faculty_id=fac.id).update({'faculty_id': None})

        # 3. Delete ONLY the User account
        if user_id:
            from models.notification import Notification
            Notification.query.filter_by(recipient_id=user_id).delete()
            Notification.query.filter_by(related_user_id=user_id).delete()

            from models.user import User
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)

        db.session.commit()
        flash(f'Faculty "{faculty_name}" has been removed. Records are preserved in History.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('faculty.list_faculty'))
