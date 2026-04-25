"""
Email notification helper.
Sends approval/rejection emails when MAIL_ENABLED=true in config.
Falls back to logging when email is not configured.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app
import logging

logger = logging.getLogger(__name__)


def send_email(to_email, subject, html_body):
    """Send an email. Returns True on success, False on failure. Never crashes the app."""
    try:
        if not current_app.config.get('MAIL_ENABLED', False):
            logger.info(f'[EMAIL DISABLED] To: {to_email} | Subject: {subject}')
            print(f'[EMAIL NOTIFICATION] To: {to_email} | Subject: {subject}')
            return True

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = to_email
        msg.attach(MIMEText(html_body, 'html'))

        server = smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT'])
        server.starttls()
        server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        logger.info(f'[EMAIL SENT] To: {to_email} | Subject: {subject}')
        return True

    except Exception as e:
        logger.error(f'[EMAIL FAILED] To: {to_email} | Error: {str(e)}')
        print(f'[EMAIL FAILED] To: {to_email} | Error: {str(e)}')
        return False


def notify_admin_new_faculty(admin_email, faculty_name, faculty_department, faculty_email, college_name):
    """Notify admin that a new faculty has registered and needs approval."""
    subject = f'[Action Required] New Faculty Registration - {faculty_name}'
    html_body = f"""
    <div style="font-family: 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #0f172a; color: white; padding: 20px; border-radius: 12px 12px 0 0; text-align: center;">
            <h2 style="margin: 0;">{college_name}</h2>
            <p style="margin: 5px 0 0; opacity: 0.8;">New Faculty Registration</p>
        </div>
        <div style="background: #f8fafc; padding: 24px; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 12px 12px;">
            <p>A new faculty member has registered and requires your approval:</p>
            <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
                <tr><td style="padding: 8px; font-weight: 600; color: #64748b;">Name:</td><td style="padding: 8px;">{faculty_name}</td></tr>
                <tr><td style="padding: 8px; font-weight: 600; color: #64748b;">Department:</td><td style="padding: 8px;">{faculty_department}</td></tr>
                <tr><td style="padding: 8px; font-weight: 600; color: #64748b;">Email:</td><td style="padding: 8px;">{faculty_email}</td></tr>
            </table>
            <p>Please login to the system to approve or reject this registration.</p>
            <p style="margin-top: 20px; font-size: 13px; color: #94a3b8;">This is an automated notification from the Smart College Management System.</p>
        </div>
    </div>
    """
    send_email(admin_email, subject, html_body)


def notify_faculty_new_student(faculty_email, student_name, student_department, student_email, student_id_proof, college_name):
    """Notify faculty that a new student has registered and needs approval."""
    subject = f'[Action Required] New Student Registration - {student_name}'
    html_body = f"""
    <div style="font-family: 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #0f172a; color: white; padding: 20px; border-radius: 12px 12px 0 0; text-align: center;">
            <h2 style="margin: 0;">{college_name}</h2>
            <p style="margin: 5px 0 0; opacity: 0.8;">New Student Registration</p>
        </div>
        <div style="background: #f8fafc; padding: 24px; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 12px 12px;">
            <p>A new student has registered in your department and requires your approval:</p>
            <table style="width: 100%; border-collapse: collapse; margin: 16px 0;">
                <tr><td style="padding: 8px; font-weight: 600; color: #64748b;">Name:</td><td style="padding: 8px;">{student_name}</td></tr>
                <tr><td style="padding: 8px; font-weight: 600; color: #64748b;">Department:</td><td style="padding: 8px;">{student_department}</td></tr>
                <tr><td style="padding: 8px; font-weight: 600; color: #64748b;">Email:</td><td style="padding: 8px;">{student_email}</td></tr>
                <tr><td style="padding: 8px; font-weight: 600; color: #64748b;">Admission No:</td><td style="padding: 8px;">{student_id_proof}</td></tr>
            </table>
            <p>Please login to the system to approve or reject this registration.</p>
            <p style="margin-top: 20px; font-size: 13px; color: #94a3b8;">This is an automated notification from the Smart College Management System.</p>
        </div>
    </div>
    """
    send_email(faculty_email, subject, html_body)


def notify_user_approved(user_email, user_name, role, approved_by_name, college_name):
    """Notify user that their registration has been approved."""
    subject = f'Registration Approved - Welcome to {college_name}'
    html_body = f"""
    <div style="font-family: 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #10b981; color: white; padding: 20px; border-radius: 12px 12px 0 0; text-align: center;">
            <h2 style="margin: 0;">Registration Approved</h2>
        </div>
        <div style="background: #f8fafc; padding: 24px; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 12px 12px;">
            <p>Dear {user_name},</p>
            <p>Your registration as <strong>{role}</strong> for <strong>{college_name}</strong> has been approved by <strong>{approved_by_name}</strong>.</p>
            <p>You can now login to the system using the username and password you registered with.</p>
            <p style="margin-top: 20px; font-size: 13px; color: #94a3b8;">This is an automated notification from the Smart College Management System.</p>
        </div>
    </div>
    """
    send_email(user_email, subject, html_body)


def notify_user_rejected(user_email, user_name, role, rejected_by_name, reason, college_name):
    """Notify user that their registration has been rejected."""
    subject = f'Registration Update - {college_name}'
    html_body = f"""
    <div style="font-family: 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #ef4444; color: white; padding: 20px; border-radius: 12px 12px 0 0; text-align: center;">
            <h2 style="margin: 0;">Registration Not Approved</h2>
        </div>
        <div style="background: #f8fafc; padding: 24px; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 12px 12px;">
            <p>Dear {user_name},</p>
            <p>Your registration as <strong>{role}</strong> for <strong>{college_name}</strong> was not approved.</p>
            <p><strong>Reason:</strong> {reason or 'No reason provided.'}</p>
            <p>If you believe this is an error, please contact the college administration office.</p>
            <p style="margin-top: 20px; font-size: 13px; color: #94a3b8;">This is an automated notification from the Smart College Management System.</p>
        </div>
    </div>
    """
    send_email(user_email, subject, html_body)
