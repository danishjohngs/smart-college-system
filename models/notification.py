"""In-app notification model for dashboard alerts."""
from datetime import datetime
from extensions import db


class Notification(db.Model):
    """In-app notifications for approval requests and system events."""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Who should see this notification

    notification_type = db.Column(db.String(30), nullable=False)
    # Values: 'faculty_registration', 'student_registration', 'approved', 'rejected'

    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)

    related_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    # The user this notification is about (the one who registered)

    is_read = db.Column(db.Boolean, default=False)
    action_taken = db.Column(db.Boolean, default=False)
    # Has the admin/faculty already approved/rejected this request?

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='notifications')
    related_user = db.relationship('User', foreign_keys=[related_user_id])

    def __repr__(self):
        return f'<Notification {self.notification_type} for User:{self.recipient_id}>'
