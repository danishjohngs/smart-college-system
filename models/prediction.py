"""
Prediction model for storing AI prediction results.
"""
from datetime import datetime
from extensions import db


class Prediction(db.Model):
    """Stores AI/ML prediction results for audit and display."""
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    college_id = db.Column(db.Integer, db.ForeignKey('colleges.id'), nullable=False)
    prediction_type = db.Column(db.String(20), nullable=False)  # 'admission' or 'performance'
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True)
    department = db.Column(db.String(50), nullable=True)
    predicted_value = db.Column(db.Float)
    confidence = db.Column(db.Float)
    parameters = db.Column(db.Text)  # JSON string of input parameters
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Prediction {self.prediction_type} value={self.predicted_value}>'
