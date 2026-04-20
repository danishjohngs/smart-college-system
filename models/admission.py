"""
AdmissionRecord model for storing historical admission data.
Used by the AI module to predict future admission trends.
"""
from extensions import db


class AdmissionRecord(db.Model):
    """Historical admission data for AI prediction training."""
    __tablename__ = 'admission_records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.Integer, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    applications_received = db.Column(db.Integer, nullable=False, default=0)
    students_admitted = db.Column(db.Integer, nullable=False, default=0)
    total_capacity = db.Column(db.Integer, nullable=False, default=60)

    def admission_rate(self):
        """Calculate admission rate as a percentage."""
        if self.applications_received == 0:
            return 0.0
        return round((self.students_admitted / self.applications_received) * 100, 2)

    def __repr__(self):
        return f'<AdmissionRecord {self.year} {self.department}: {self.students_admitted}/{self.applications_received}>'
