"""
Student Removal Request routes — Faculty submits → Admin approves/rejects → Faculty confirms.
"""
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.removal_request import RemovalRequest
from models.student import Student
from models.faculty import Faculty
from models.user import User
from models.notification import Notification
from routes.auth import admin_required

removal_bp = Blueprint('removal', __name__)


@removal_bp.route('/removal-requests')
@login_required
def list_requests():
    """List removal requests. Admin sees all, faculty sees their own."""
    if not (current_user.is_admin() or current_user.is_faculty()):
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))

    status_filter = request.args.get('status', 'all')

    if current_user.is_admin():
        query = RemovalRequest.query
    else:
        query = RemovalRequest.query.filter_by(requested_by=current_user.id)

    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    requests_list = query.order_by(RemovalRequest.created_at.desc()).all()

    pending_count = 0
    if current_user.is_admin():
        pending_count = RemovalRequest.query.filter_by(status='pending').count()

    return render_template('removal/list.html',
                           requests=requests_list,
                           status_filter=status_filter,
                           pending_count=pending_count)


@removal_bp.route('/removal-requests/new/<int:student_id>', methods=['GET', 'POST'])
@login_required
def submit_request(student_id):
    """Faculty submits a removal request for a student."""
    if not (current_user.is_faculty() or current_user.is_admin()):
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))

    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        reason = request.form.get('reason', '').strip()
        parent_phone = request.form.get('parent_phone', '').strip()
        student_class = request.form.get('student_class', '').strip()
        additional_remarks = request.form.get('additional_remarks', '').strip()

        errors = []
        if not reason or len(reason) < 20:
            errors.append('Reason must be at least 20 characters with specific details.')
        if not parent_phone or len(parent_phone) < 10:
            errors.append('Parent/Guardian phone number is required (min 10 digits).')
        if not student_class:
            errors.append('Student class/section is required.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('removal/submit.html', student=student)

        try:
            removal_req = RemovalRequest(
                requested_by=current_user.id,
                student_id=student.id,
                student_name=student.name,
                student_roll_number=student.roll_number,
                student_department=student.department,
                student_semester=student.semester,
                student_phone=student.phone or '',
                student_email=student.email or '',
                parent_phone=parent_phone,
                student_class=student_class,
                reason=reason,
                additional_remarks=additional_remarks,
                status='pending'
            )
            db.session.add(removal_req)

            # Notify all admins (in-app only, NO email)
            admins = User.query.filter_by(role='admin', status='approved').all()
            requester_name = current_user.full_name or current_user.username
            for admin in admins:
                notif = Notification(
                    recipient_id=admin.id,
                    notification_type='removal_request',
                    title='Student Removal Request',
                    message=f'{requester_name} has requested removal of student {student.name} ({student.roll_number}) from {student.department}. Reason: {reason[:80]}...',
                    related_user_id=current_user.id
                )
                db.session.add(notif)

            db.session.commit()
            flash(f'Removal request for "{student.name}" submitted to the administrator.', 'success')
            return redirect(url_for('removal.list_requests'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')

    return render_template('removal/submit.html', student=student)


@removal_bp.route('/removal-requests/view/<int:request_id>')
@login_required
def view_request(request_id):
    """View detailed removal request."""
    removal_req = RemovalRequest.query.get_or_404(request_id)

    if not current_user.is_admin() and removal_req.requested_by != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('removal.list_requests'))

    return render_template('removal/view.html', removal_request=removal_req)


@removal_bp.route('/removal-requests/approve/<int:request_id>', methods=['POST'])
@login_required
@admin_required
def approve_request(request_id):
    """Admin approves a removal request. Student is IMMEDIATELY removed."""
    removal_req = RemovalRequest.query.get_or_404(request_id)

    if removal_req.status != 'pending':
        flash('This request has already been processed.', 'warning')
        return redirect(url_for('removal.list_requests'))

    admin_remarks = request.form.get('admin_remarks', '').strip()

    try:
        removal_req.status = 'approved'
        removal_req.reviewed_by = current_user.id
        removal_req.reviewed_at = datetime.utcnow()
        removal_req.admin_remarks = admin_remarks or 'Approved.'

        # IMMEDIATELY delete student and data
        student = Student.query.get(removal_req.student_id)
        if student:
            student_user_id = student.user_id
            
            # Delete notifications and user account
            if student_user_id:
                Notification.query.filter_by(recipient_id=student_user_id).delete()
                Notification.query.filter_by(related_user_id=student_user_id).delete()
                user = User.query.get(student_user_id)
                if user:
                    db.session.delete(user)
                    
            # Delete student (cascade deletes attendance, grades, predictions)
            db.session.delete(student)

        admin_name = current_user.full_name or current_user.username
        # Notify faculty
        notif = Notification(
            recipient_id=removal_req.requested_by,
            notification_type='removal_approved',
            title='Removal Request Approved',
            message=f'Your removal request for {removal_req.student_name} ({removal_req.student_roll_number}) has been approved and executed. The student has been permanently removed from the system by {admin_name}.',
            related_user_id=current_user.id
        )
        db.session.add(notif)

        db.session.commit()
        flash('Request APPROVED. Student permanently removed. Faculty has been notified.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('removal.list_requests'))


@removal_bp.route('/removal-requests/reject/<int:request_id>', methods=['POST'])
@login_required
@admin_required
def reject_request(request_id):
    """Admin rejects a removal request with reason."""
    removal_req = RemovalRequest.query.get_or_404(request_id)

    if removal_req.status != 'pending':
        flash('This request has already been processed.', 'warning')
        return redirect(url_for('removal.list_requests'))

    admin_remarks = request.form.get('admin_remarks', '').strip()
    if not admin_remarks or len(admin_remarks) < 5:
        flash('Please provide a reason for rejection (at least 5 characters).', 'danger')
        return redirect(url_for('removal.view_request', request_id=request_id))

    try:
        removal_req.status = 'rejected'
        removal_req.reviewed_by = current_user.id
        removal_req.reviewed_at = datetime.utcnow()
        removal_req.admin_remarks = admin_remarks

        admin_name = current_user.full_name or current_user.username
        # Notify faculty
        notif = Notification(
            recipient_id=removal_req.requested_by,
            notification_type='removal_rejected',
            title='Removal Request Rejected',
            message=f'Your removal request for {removal_req.student_name} ({removal_req.student_roll_number}) has been rejected by {admin_name}. Reason: {admin_remarks}. The student will remain active in the system.',
            related_user_id=current_user.id
        )
        db.session.add(notif)

        db.session.commit()
        flash('Request REJECTED. Faculty has been notified.', 'info')

    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('removal.list_requests'))



