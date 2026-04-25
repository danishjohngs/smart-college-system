"""
Authentication routes: login, register, logout.
Uses Flask-Login for session management.
Includes hierarchical user registration approval workflow:
  - Admin approves Faculty
  - Faculty approves Students (same department)
  - Admin can also approve Students (as backup)
"""
from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.user import User

auth_bp = Blueprint('auth', __name__)


def admin_required(f):
    """Decorator to restrict access to admin users only."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


def faculty_required(f):
    """Decorator to restrict access to faculty and admin users."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not (current_user.is_admin() or current_user.is_faculty()):
            flash('Access denied. Faculty privileges required.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================
# LOGIN
# ============================================================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login with approval status check."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # CHECK APPROVAL STATUS BEFORE ALLOWING LOGIN
            if user.status == 'pending':
                if user.role == 'faculty':
                    flash('Your registration is pending approval from the administrator. Please wait.', 'warning')
                elif user.role == 'student':
                    flash('Your registration is pending approval from your department faculty. Please wait.', 'warning')
                else:
                    flash('Your account is pending approval.', 'warning')
                return render_template('auth/login.html')
            elif user.status == 'rejected':
                reason = user.rejection_reason or 'No reason provided'
                flash(f'Your registration was not approved. Reason: {reason}. Please contact the administration.', 'danger')
                return render_template('auth/login.html')
            elif user.status == 'approved':
                login_user(user)
                flash(f'Welcome, {user.full_name or user.username}!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('auth/login.html')


# ============================================================
# PUBLIC SELF-REGISTRATION (anyone can register)
# ============================================================
from werkzeug.utils import secure_filename
import os
import uuid
from flask import current_app
from models.college import College

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route('/register', methods=['GET', 'POST'])
def public_register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    departments = ['Computer Science', 'Electronics', 'Mechanical', 'Electrical', 'Civil']

    if request.method == 'POST':
        role = request.form.get('role', 'student')
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        gender = request.form.get('gender', '').strip()
        date_of_birth_str = request.form.get('date_of_birth', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        errors = []
        if not full_name: errors.append('Full name is required.')
        if not email or '@' not in email: errors.append('Valid email is required.')
        if not phone: errors.append('Phone number is required.')
        if not gender: errors.append('Gender is required.')
        if not date_of_birth_str: errors.append('Date of birth is required.')
        if not username or len(username) < 3: errors.append('Username must be at least 3 characters.')
        if not password or len(password) < 8: errors.append('Password must be at least 8 characters.')
        if password != confirm_password: errors.append('Passwords do not match.')

        if User.query.filter_by(username=username).first(): errors.append('Username already taken.')
        if User.query.filter_by(email=email).first(): errors.append('Email already registered.')

        # Profile Photo
        profile_photo = request.files.get('profile_photo')
        photo_filename = None
        if profile_photo and profile_photo.filename:
            if allowed_file(profile_photo.filename):
                ext = profile_photo.filename.rsplit('.', 1)[1].lower()
                photo_filename = f"{uuid.uuid4().hex}.{ext}"
                profile_photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], photo_filename))
            else:
                errors.append('Invalid profile photo format.')

        college_id = None
        status = 'pending'

        date_of_birth = None
        if date_of_birth_str:
            from datetime import datetime
            try:
                date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append('Invalid date format for Date of Birth.')

        if role == 'admin':
            college_name = request.form.get('college_name', '').strip()
            college_location = request.form.get('college_location', '').strip()
            website = request.form.get('website', '').strip()
            designation = request.form.get('admin_designation', '').strip()

            if not college_name: errors.append('College name is required.')
            if not college_location: errors.append('College location is required.')
            if not designation: errors.append('Designation is required.')

            if not errors:
                user = User(
                    full_name=full_name, email=email, phone=phone, gender=gender,
                    username=username, role='admin', status='approved',
                    admin_designation=designation, profile_photo=photo_filename,
                    date_of_birth=date_of_birth
                )
                user.set_password(password)
                db.session.add(user)
                db.session.flush() # Get user ID
                
                college_code = College.generate_unique_code(college_name)
                college = College(
                    name=college_name, location=college_location, website=website,
                    college_code=college_code, created_by=user.id
                )
                db.session.add(college)
                db.session.flush()
                
                user.college_id = college.id
                db.session.commit()
                
                try:
                    from utils.email_notifications import notify_admin_college_registered
                    notify_admin_college_registered(email, college_name, college_code)
                except: pass

                flash(f'College registered successfully! Your unique college code is: {college_code}. Share this code with your faculty and students. You can now login.', 'success')
                return redirect(url_for('auth.login'))

        elif role == 'faculty':
            department = request.form.get('department', '').strip()
            employee_id = request.form.get('employee_id', '').strip()
            designation = request.form.get('designation', '').strip()
            qualification = request.form.get('qualification', '').strip()
            specialization = request.form.get('specialization', '').strip()
            years_of_experience = request.form.get('years_of_experience', '')
            college_code = request.form.get('college_code', '').strip()

            if not department: errors.append('Department is required.')
            if not employee_id: errors.append('Employee ID is required.')
            if not designation: errors.append('Designation is required.')
            if not qualification: errors.append('Highest qualification is required.')
            if not years_of_experience: errors.append('Years of experience is required.')
            if not college_code: errors.append('College code is required.')

            college = College.query.filter_by(college_code=college_code).first()
            if not college:
                errors.append('Invalid college code. Please contact your college administrator for the correct code.')
            else:
                college_id = college.id

            if not errors:
                user = User(
                    full_name=full_name, email=email, phone=phone, gender=gender,
                    username=username, role='faculty', status='pending', college_id=college_id,
                    department=department, id_proof_number=employee_id, designation=designation,
                    qualification=qualification, specialization=specialization,
                    years_of_experience=int(years_of_experience), date_of_birth=date_of_birth,
                    profile_photo=photo_filename
                )
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                
                _send_registration_notifications(user, college)
                
                flash(f'Registration submitted! Your request has been sent to the administrator of {college.name}. You will receive an email once approved.', 'success')
                return redirect(url_for('auth.login'))

        elif role == 'student':
            department = request.form.get('department', '').strip()
            roll_number = request.form.get('roll_number', '').strip()
            semester = request.form.get('semester', '')
            admission_year = request.form.get('admission_year', '')
            graduation_year = request.form.get('graduation_year', '')
            programme = request.form.get('programme', '').strip()
            blood_group = request.form.get('blood_group', '').strip()
            parent_name = request.form.get('parent_name', '').strip()
            parent_phone = request.form.get('parent_phone', '').strip()
            address = request.form.get('address', '').strip()
            college_code = request.form.get('college_code', '').strip()

            if not department: errors.append('Department is required.')
            if not roll_number: errors.append('Admission Number is required.')
            if not semester: errors.append('Current semester is required.')
            if not admission_year: errors.append('Batch/admission year is required.')
            if not graduation_year: errors.append('Expected graduation year is required.')
            if not programme: errors.append('Programme name is required.')
            if not parent_name: errors.append('Parent name is required.')
            if not parent_phone or len(parent_phone) < 10: errors.append('Parent phone (min 10 digits) is required.')
            if not college_code: errors.append('College code is required.')

            college = College.query.filter_by(college_code=college_code).first()
            if not college:
                errors.append('Invalid college code.')
            else:
                college_id = college.id

            if not errors:
                user = User(
                    full_name=full_name, email=email, phone=phone, gender=gender,
                    username=username, role='student', status='pending', college_id=college_id,
                    department=department, id_proof_number=roll_number, semester=int(semester),
                    admission_year=int(admission_year), graduation_year=int(graduation_year),
                    programme=programme, blood_group=blood_group, parent_name=parent_name,
                    parent_phone=parent_phone, address=address, date_of_birth=date_of_birth,
                    profile_photo=photo_filename
                )
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                
                _send_registration_notifications(user, college)
                
                flash(f'Registration submitted! Your request has been sent to the faculty of {department} at {college.name}.', 'success')
                return redirect(url_for('auth.login'))

        if errors:
            for e in errors:
                flash(e, 'danger')

    return render_template('auth/public_register.html', departments=departments)


def _send_registration_notifications(user, college):
    try:
        from utils.email_notifications import notify_admin_new_faculty, notify_faculty_new_student
        from models.notification import Notification

        if user.role == 'faculty':
            # Notify ALL approved admins OF THAT COLLEGE
            admins = User.query.filter_by(role='admin', status='approved', college_id=college.id).all()
            for admin in admins:
                notif = Notification(
                    recipient_id=admin.id,
                    notification_type='faculty_registration',
                    title=f'New Faculty Registration',
                    message=f'{user.full_name} ({user.department}) has registered as faculty and needs your approval.',
                    related_user_id=user.id
                )
                db.session.add(notif)
                if admin.email:
                    notify_admin_new_faculty(admin.email, user.full_name, user.department, user.email, college.name)

        elif user.role == 'student':
            # Notify ALL approved faculty in the SAME department OF THAT COLLEGE
            from models.faculty import Faculty
            dept_faculty = Faculty.query.filter_by(department=user.department, college_id=college.id).all()
            notified_ids = set()

            for fac in dept_faculty:
                if fac.user_id and fac.user_id not in notified_ids:
                    fac_user = User.query.get(fac.user_id)
                    if fac_user and fac_user.status == 'approved':
                        notif = Notification(
                            recipient_id=fac_user.id,
                            notification_type='student_registration',
                            title='New Student Registration',
                            message=f'{user.full_name} ({user.department}) has registered as a student and needs your approval.',
                            related_user_id=user.id
                        )
                        db.session.add(notif)
                        notified_ids.add(fac_user.id)
                        if fac_user.email:
                            notify_faculty_new_student(fac_user.email, user.full_name, user.department, user.email, user.id_proof_number, college.name)

            # Also notify admins OF THAT COLLEGE as backup
            admins = User.query.filter_by(role='admin', status='approved', college_id=college.id).all()
            for admin in admins:
                notif = Notification(
                    recipient_id=admin.id,
                    notification_type='student_registration',
                    title='New Student Registration',
                    message=f'{user.full_name} ({user.department}) has registered as a student.',
                    related_user_id=user.id
                )
                db.session.add(notif)

        db.session.commit()
    except Exception as e:
        print(f'[NOTIFICATION ERROR] {e}')


# ============================================================
# ADMIN: CREATE USER (direct, auto-approved)
# ============================================================
@auth_bp.route('/admin/register', methods=['GET', 'POST'])
@login_required
def admin_register():
    """Register a new user (admin only). User is auto-approved."""
    if not current_user.is_admin():
        flash('Only administrators can create users directly.', 'danger')
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'student')

        # Validation
        errors = []
        if not username:
            errors.append('Username is required.')
        if not email:
            errors.append('Email is required.')
        if not password:
            errors.append('Password is required.')
        if password != confirm_password:
            errors.append('Passwords do not match.')
        if len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        if role not in ('admin', 'faculty', 'student'):
            errors.append('Invalid role selected.')
        if User.query.filter_by(username=username).first():
            errors.append('Username already exists.')
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html')

        try:
            user = User(
                username=username,
                email=email,
                role=role,
                status='approved',
                approved_by=current_user.id,
                approved_at=datetime.utcnow()
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash(f'User "{username}" created successfully as {role} (auto-approved).', 'success')
            return redirect(url_for('dashboard.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating user: {str(e)}', 'danger')

    return render_template('auth/register.html')


# ============================================================
# APPROVAL MANAGEMENT (Admin + Faculty)
# ============================================================
@auth_bp.route('/approvals')
@login_required
def approval_list():
    """Show pending registrations the current user can approve.
    Admin: sees faculty/admin registrations + all students.
    Faculty: sees only students from their department.
    """
    if not (current_user.is_admin() or current_user.is_faculty()):
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))

    status_filter = request.args.get('status', 'pending')

    if current_user.is_admin():
        if status_filter == 'all':
            registrations = User.query.filter(User.id != current_user.id, User.college_id == current_user.college_id).order_by(User.created_at.desc()).all()
        else:
            registrations = User.query.filter_by(status=status_filter, college_id=current_user.college_id).filter(
                User.id != current_user.id
            ).order_by(User.created_at.desc()).all()
    elif current_user.is_faculty():
        # Faculty sees ONLY students from their department
        from models.faculty import Faculty
        fac = Faculty.query.filter_by(user_id=current_user.id).first()
        dept = fac.department if fac else current_user.department

        if status_filter == 'all':
            registrations = User.query.filter_by(role='student', department=dept, college_id=current_user.college_id).filter(
                User.id != current_user.id
            ).order_by(User.created_at.desc()).all()
        else:
            registrations = User.query.filter_by(
                role='student', department=dept, status=status_filter, college_id=current_user.college_id
            ).filter(User.id != current_user.id).order_by(User.created_at.desc()).all()

    # Calculate pending count for current user's scope
    pending_count = _get_pending_count_for_user(current_user)

    return render_template('auth/approvals.html',
                           registrations=registrations,
                           status_filter=status_filter,
                           pending_count=pending_count)


@auth_bp.route('/approve/<int:user_id>', methods=['POST'])
@login_required
def approve_user(user_id):
    """Approve a registration. Permission: Admin for faculty/admin, Faculty for students."""
    user = User.query.get_or_404(user_id)

    # Permission checks
    if current_user.is_admin():
        if user.college_id != current_user.college_id:
            flash('You can only approve users for your own college.', 'danger')
            return redirect(url_for('auth.approval_list'))
    elif current_user.is_faculty():
        if user.role != 'student':
            flash('Faculty can only approve student registrations.', 'danger')
            return redirect(url_for('auth.approval_list'))
        if user.college_id != current_user.college_id:
            flash('You can only approve students from your college.', 'danger')
            return redirect(url_for('auth.approval_list'))
        from models.faculty import Faculty
        fac = Faculty.query.filter_by(user_id=current_user.id).first()
        if fac and fac.department != user.department:
            flash('You can only approve students from your department.', 'danger')
            return redirect(url_for('auth.approval_list'))
    else:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))

    if user.status != 'pending':
        flash(f'User "{user.username}" is already {user.status}.', 'warning')
        return redirect(url_for('auth.approval_list'))

    user.status = 'approved'
    user.approved_by = current_user.id
    user.approved_at = datetime.utcnow()
    user.rejection_reason = None

    # Auto-create Student record
    if user.role == 'student':
        from models.student import Student
        existing = Student.query.filter_by(user_id=user.id).first()
        if not existing:
            student = Student(
                user_id=user.id,
                college_id=user.college_id,
                name=user.full_name or user.username,
                roll_number=user.id_proof_number or f'STU{user.id:04d}',
                email=user.email,
                phone=user.phone,
                department=user.department or 'Computer Science',
                semester=user.semester or 1,
                admission_year=user.admission_year or datetime.utcnow().year,
                date_of_birth=user.date_of_birth,
                gender=user.gender,
                address=user.address,
                status='active'
            )
            db.session.add(student)

    # Auto-create Faculty record
    elif user.role == 'faculty':
        from models.faculty import Faculty
        existing = Faculty.query.filter_by(user_id=user.id).first()
        if not existing:
            faculty = Faculty(
                user_id=user.id,
                college_id=user.college_id,
                name=user.full_name or user.username,
                employee_id=user.id_proof_number or f'FAC{user.id:04d}',
                email=user.email,
                phone=user.phone,
                department=user.department or 'Computer Science',
                designation=user.designation or 'Assistant Professor',
                qualification=user.qualification or ''
            )
            db.session.add(faculty)

    # Mark related notifications as action_taken
    from models.notification import Notification
    Notification.query.filter_by(related_user_id=user.id, action_taken=False).update({'action_taken': True})

    # Create approval notification for the user
    approver_name = current_user.full_name or current_user.username
    notif = Notification(
        recipient_id=user.id,
        notification_type='approved',
        title='Registration Approved',
        message=f'Your registration as {user.role} has been approved by {approver_name}. You can now login.',
        related_user_id=current_user.id
    )
    db.session.add(notif)

    # Send approval email
    try:
        from utils.email_notifications import notify_user_approved
        notify_user_approved(user.email, user.full_name or user.username, user.role, approver_name, current_user.college.name)
    except Exception:
        pass

    db.session.commit()
    flash(f'{user.full_name or user.username} has been APPROVED as {user.role}.', 'success')
    return redirect(url_for('auth.approval_list'))


@auth_bp.route('/reject/<int:user_id>', methods=['POST'])
@login_required
def reject_user(user_id):
    """Reject a registration."""
    user = User.query.get_or_404(user_id)

    # Permission checks (same as approve)
    if current_user.is_admin():
        pass
    elif current_user.is_faculty():
        if user.role != 'student':
            flash('Faculty can only manage student registrations.', 'danger')
            return redirect(url_for('auth.approval_list'))
    else:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))

    reason = request.form.get('reason', '').strip() or 'No reason provided'

    user.status = 'rejected'
    user.approved_by = current_user.id
    user.approved_at = datetime.utcnow()
    user.rejection_reason = reason

    # Mark related notifications as action_taken
    from models.notification import Notification
    Notification.query.filter_by(related_user_id=user.id, action_taken=False).update({'action_taken': True})

    # Send rejection email
    try:
        from utils.email_notifications import notify_user_rejected
        rejector_name = current_user.full_name or current_user.username
        notify_user_rejected(user.email, user.full_name or user.username, user.role, rejector_name, reason, current_user.college.name)
    except Exception:
        pass

    db.session.commit()
    flash(f'{user.full_name or user.username} has been REJECTED.', 'warning')
    return redirect(url_for('auth.approval_list'))


@auth_bp.route('/revoke/<int:user_id>', methods=['POST'])
@login_required
def revoke_user(user_id):
    """Revoke an approved user's access."""
    if not current_user.is_admin():
        flash('Only admins can revoke access.', 'danger')
        return redirect(url_for('dashboard.index'))

    user = User.query.get_or_404(user_id)
    if user.is_admin():
        flash('Cannot revoke admin accounts.', 'danger')
        return redirect(url_for('auth.approval_list'))

    reason = request.form.get('reason', '').strip()
    user.status = 'rejected'
    user.approved_by = current_user.id
    user.approved_at = datetime.utcnow()
    user.rejection_reason = reason or 'Access revoked by administrator'

    db.session.commit()
    flash(f'Access revoked for "{user.full_name or user.username}".', 'warning')
    return redirect(url_for('auth.approval_list'))


# ============================================================
# NOTIFICATION ROUTES
# ============================================================
@auth_bp.route('/notifications')
@login_required
def notifications_list():
    """View all notifications for the current user."""
    from models.notification import Notification
    notifications = Notification.query.filter_by(
        recipient_id=current_user.id
    ).order_by(Notification.created_at.desc()).limit(50).all()

    # Mark as read
    Notification.query.filter_by(recipient_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()

    return render_template('auth/notifications.html', notifications=notifications)


@auth_bp.route('/notifications/mark-read', methods=['POST'])
@login_required
def mark_notifications_read():
    """Mark all notifications as read."""
    from models.notification import Notification
    Notification.query.filter_by(recipient_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return redirect(request.referrer or url_for('dashboard.index'))

# ============================================================
# DELETE PENDING/REJECTED REGISTRATIONS
# ============================================================
@auth_bp.route('/admin/delete-registration/<int:user_id>', methods=['POST'])
@login_required
def delete_registration(user_id):
    """Delete a pending or rejected registration to free username/email."""
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))

    user = User.query.get_or_404(user_id)

    if user.status == 'approved':
        flash('Cannot delete an approved account from here. Use Student or Faculty management.', 'danger')
        return redirect(url_for('auth.approval_list'))

    try:
        user_name = user.full_name or user.username

        # Clean up any accidentally created Student/Faculty records
        from models.student import Student
        from models.faculty import Faculty
        Student.query.filter_by(user_id=user.id).delete()
        Faculty.query.filter_by(user_id=user.id).delete()

        # Clean up notifications
        from models.notification import Notification
        Notification.query.filter_by(recipient_id=user.id).delete()
        Notification.query.filter_by(related_user_id=user.id).delete()

        # Fully delete the user (nothing to archive — they were never active)
        db.session.delete(user)
        db.session.commit()

        flash(f'Registration for "{user_name}" deleted. Username and email are now available.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('auth.approval_list'))


# ============================================================
# PROFILE
# ============================================================
@auth_bp.route('/profile/update-email', methods=['POST'])
@login_required
def update_email():
    """Allow any user to update their own email address."""
    new_email = request.form.get('email', '').strip()
    
    if not new_email or '@' not in new_email or '.' not in new_email:
        flash('Please enter a valid email address.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Check if email is already taken by someone else
    existing = User.query.filter(User.email == new_email, User.id != current_user.id).first()
    if existing:
        flash('This email is already registered to another account.', 'danger')
        return redirect(url_for('dashboard.index'))
    
    try:
        current_user.email = new_email
        
        # Also update the linked Student or Faculty record email
        if current_user.is_student():
            from models.student import Student
            student = Student.query.filter_by(user_id=current_user.id).first()
            if student:
                student.email = new_email
        elif current_user.is_faculty():
            from models.faculty import Faculty
            faculty = Faculty.query.filter_by(user_id=current_user.id).first()
            if faculty:
                faculty.email = new_email
        
        db.session.commit()
        flash(f'Email updated to {new_email}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating email: {str(e)}', 'danger')
    
    return redirect(url_for('dashboard.index'))


# ============================================================
# LOGOUT
# ============================================================
@auth_bp.route('/logout')
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


# ============================================================
# HELPER
# ============================================================
def _get_pending_count_for_user(user):
    """Get the pending approval count relevant to the user's role."""
    if user.is_admin():
        return User.query.filter_by(status='pending', college_id=user.college_id).count()
    elif user.is_faculty():
        from models.faculty import Faculty
        fac = Faculty.query.filter_by(user_id=user.id).first()
        dept = fac.department if fac else user.department
        if dept:
            return User.query.filter_by(status='pending', role='student', department=dept, college_id=user.college_id).count()
    return 0
