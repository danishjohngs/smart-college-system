"""Student Removal Request model for faculty-to-admin approval workflow."""
from datetime import datetime
from extensions import db


class RemovalRequest(db.Model):
    """Tracks student removal requests from faculty, requiring admin approval."""
    __tablename__ = 'removal_requests'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    requested_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)

    # Student details captured at request time (preserved even after student is removed)
    student_name = db.Column(db.String(100), nullable=False)
    student_roll_number = db.Column(db.String(20), nullable=False)
    student_department = db.Column(db.String(50), nullable=False)
    student_semester = db.Column(db.Integer)
    student_phone = db.Column(db.String(15))
    student_email = db.Column(db.String(120))
    parent_phone = db.Column(db.String(15), nullable=False)
    student_class = db.Column(db.String(50), nullable=False)

    reason = db.Column(db.Text, nullable=False)
    additional_remarks = db.Column(db.Text)

    status = db.Column(db.String(20), nullable=False, default='pending')
    # Values: 'pending', 'approved', 'rejected'

    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    admin_remarks = db.Column(db.Text, nullable=True)

    # After admin approves, faculty decides what to do
    faculty_action = db.Column(db.String(20), nullable=True)
    # Values: None (not yet decided), 'removed', 'stayed'
    faculty_action_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    requester = db.relationship('User', foreign_keys=[requested_by], backref='removal_requests_made')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])
    student = db.relationship('Student', backref='removal_requests')

    def __repr__(self):
        return f'<RemovalRequest {self.student_name} status={self.status}>'
