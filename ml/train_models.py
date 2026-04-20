"""
Train ML Models Script
Trains both admission and performance prediction models using data from the database.
Run after seed_data.py populates the database.

Usage: python -c "from ml.train_models import train_all; train_all()"
Or run directly as part of seed_data.py
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def train_all():
    """Train all ML models using data from the database."""
    from app import create_app
    from models.admission import AdmissionRecord
    from models.student import Student
    from models.grade import Grade
    from ml.admission_predictor import AdmissionPredictor
    from ml.performance_predictor import PerformancePredictor

    app = create_app()

    with app.app_context():
        print("=" * 50)
        print("Training ML Models")
        print("=" * 50)

        # 1. Train Admission Predictor
        print("\n[1/2] Training Admission Predictor...")
        records = AdmissionRecord.query.all()
        if records:
            training_data = [{
                'year': r.year,
                'department': r.department,
                'applications': r.applications_received,
                'admitted': r.students_admitted
            } for r in records]

            predictor = AdmissionPredictor()
            score = predictor.train(training_data)
            print(f"  ✓ Admission model trained. R² Score: {score:.4f}")
            print(f"  ✓ Training samples: {len(training_data)}")
        else:
            print("  ✗ No admission records found. Skipping.")

        # 2. Train Performance Predictor
        print("\n[2/2] Training Performance Predictor...")
        students = Student.query.all()
        if students:
            training_data = []
            for student in students:
                attendance_pct = student.get_attendance_percentage()
                past_cgpa = student.cgpa or 0.0
                grades = Grade.query.filter_by(student_id=student.id).all()
                avg_internal = sum(g.internal_marks for g in grades if g.internal_marks) / len(grades) if grades else 0

                # Determine category
                if past_cgpa >= 8.0:
                    category = 3
                elif past_cgpa >= 6.0:
                    category = 2
                elif past_cgpa >= 4.0:
                    category = 1
                else:
                    category = 0

                training_data.append({
                    'attendance_pct': attendance_pct,
                    'past_cgpa': past_cgpa,
                    'internal_marks': avg_internal,
                    'category': category
                })

            predictor = PerformancePredictor()
            accuracy = predictor.train(training_data)
            print(f"  ✓ Performance model trained. Accuracy: {accuracy:.4f}")
            print(f"  ✓ Training samples: {len(training_data)}")
        else:
            print("  ✗ No student records found. Skipping.")

        print("\n" + "=" * 50)
        print("Model training complete!")
        print("=" * 50)


if __name__ == '__main__':
    train_all()
