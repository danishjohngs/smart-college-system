"""
College model — each college registered in the system.
"""
import random
import string
from datetime import datetime
from extensions import db


class College(db.Model):
    """Represents a registered college/institution."""
    __tablename__ = 'colleges'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    website = db.Column(db.String(200), nullable=True)
    
    # Unique college code — used by faculty and students to register
    college_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Admin who created this college
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_college')

    @staticmethod
    def generate_unique_code(college_name):
        """
        Generate a unique college code.
        Format: ABC-X7K9M2 (3-letter prefix from name + dash + 6 random alphanumeric)
        """
        # Create prefix from college name (first letter of each word, max 3)
        words = college_name.strip().split()
        prefix = ''.join(w[0].upper() for w in words if w)[:3]
        if len(prefix) < 3:
            prefix = prefix.ljust(3, 'X')  # Pad with X if less than 3 words
        
        # Generate random suffix until unique
        for _ in range(100):  # Max 100 attempts
            suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            code = f"{prefix}-{suffix}"
            if not College.query.filter_by(college_code=code).first():
                return code
        
        # Fallback: use timestamp
        import time
        return f"{prefix}-{int(time.time()) % 1000000}"

    def __repr__(self):
        return f'<College {self.name} ({self.college_code})>'
