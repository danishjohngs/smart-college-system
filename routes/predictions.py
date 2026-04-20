"""
AI Prediction routes — admission trends and student performance prediction.
"""
import json
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.prediction import Prediction
from models.student import Student
from models.admission import AdmissionRecord
from models.attendance import Attendance
from models.grade import Grade

predictions_bp = Blueprint('predictions', __name__)


@predictions_bp.route('/predictions/admission', methods=['GET', 'POST'])
@login_required
def admission_prediction():
    """Predict future admission trends using historical data."""
    if not (current_user.is_admin() or current_user.is_faculty()):
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))

    departments = Student.DEPARTMENTS
    prediction_result = None
    historical_data = []
    error_message = None

    # Get historical data for charts
    records = AdmissionRecord.query.order_by(AdmissionRecord.year).all()
    for r in records:
        historical_data.append({
            'year': r.year,
            'department': r.department,
            'applications': r.applications_received,
            'admitted': r.students_admitted,
            'capacity': r.total_capacity
        })

    if request.method == 'POST':
        try:
            year = int(request.form.get('year', 2027))
            department = request.form.get('department', '')
            applications = int(request.form.get('applications', 100))

            if not department:
                flash('Please select a department.', 'danger')
                return render_template('predictions/admission.html',
                                       departments=departments,
                                       historical_data=json.dumps(historical_data))

            # Import and use admission predictor
            from ml.admission_predictor import AdmissionPredictor
            predictor = AdmissionPredictor()

            # Train if model doesn't exist
            model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                      'ml', 'saved_models', 'admission_model.pkl')
            if not os.path.exists(model_path):
                # Train on historical data
                training_data = []
                for r in records:
                    training_data.append({
                        'year': r.year,
                        'department': r.department,
                        'applications': r.applications_received,
                        'admitted': r.students_admitted
                    })
                if len(training_data) < 5:
                    flash('Not enough historical data to train the model. Need at least 5 records.', 'warning')
                    return render_template('predictions/admission.html',
                                           departments=departments,
                                           historical_data=json.dumps(historical_data))
                predictor.train(training_data)

            # Make prediction
            result = predictor.predict(year, department, applications)

            prediction_result = {
                'year': year,
                'department': department,
                'applications': applications,
                'predicted_admissions': round(result['predicted_admissions']),
                'confidence': round(result['confidence'] * 100, 1)
            }

            # Save prediction to database
            pred = Prediction(
                prediction_type='admission',
                department=department,
                predicted_value=result['predicted_admissions'],
                confidence=result['confidence'],
                parameters=json.dumps({
                    'year': year,
                    'department': department,
                    'applications': applications
                })
            )
            db.session.add(pred)
            db.session.commit()

            flash('Admission prediction generated successfully.', 'success')

        except Exception as e:
            error_message = str(e)
            flash(f'Prediction error: {error_message}', 'danger')

    return render_template('predictions/admission.html',
                           departments=departments,
                           prediction_result=prediction_result,
                           historical_data=json.dumps(historical_data),
                           error_message=error_message)


@predictions_bp.route('/predictions/performance', methods=['GET', 'POST'])
@login_required
def performance_prediction():
    """Predict student performance using ML."""
    if not (current_user.is_admin() or current_user.is_faculty()):
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))

    students = Student.query.filter_by(status='active').order_by(Student.name).all()
    prediction_result = None
    all_predictions = []
    error_message = None

    if request.method == 'POST':
        action = request.form.get('action', 'single')

        try:
            from ml.performance_predictor import PerformancePredictor
            predictor = PerformancePredictor()

            # Train if model doesn't exist
            model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                      'ml', 'saved_models', 'performance_model.pkl')
            if not os.path.exists(model_path):
                _train_performance_model(predictor)

            if action == 'single':
                student_id = request.form.get('student_id')
                if not student_id:
                    flash('Please select a student.', 'danger')
                    return render_template('predictions/performance.html', students=students)

                student = Student.query.get(int(student_id))
                if not student:
                    flash('Student not found.', 'danger')
                    return render_template('predictions/performance.html', students=students)

                # Get student's data
                attendance_pct = student.get_attendance_percentage()
                past_cgpa = student.cgpa or 0.0

                # Average internal marks
                grades = Grade.query.filter_by(student_id=student.id).all()
                avg_internal = sum(g.internal_marks for g in grades if g.internal_marks) / len(grades) if grades else 0

                result = predictor.predict(attendance_pct, past_cgpa, avg_internal)

                prediction_result = {
                    'student': student,
                    'attendance_pct': attendance_pct,
                    'past_cgpa': past_cgpa,
                    'avg_internal': round(avg_internal, 1),
                    'risk_level': result['risk_level'],
                    'confidence': round(result['confidence'] * 100, 1),
                    'category': result['category']
                }

                # Save prediction
                pred = Prediction(
                    prediction_type='performance',
                    student_id=student.id,
                    department=student.department,
                    predicted_value=float(result['category']),
                    confidence=result['confidence'],
                    parameters=json.dumps({
                        'attendance_pct': attendance_pct,
                        'past_cgpa': past_cgpa,
                        'avg_internal': round(avg_internal, 1)
                    })
                )
                db.session.add(pred)
                db.session.commit()

                flash(f'Performance prediction for {student.name}: {result["risk_level"]}', 'success')

            elif action == 'bulk':
                # Predict for all active students
                for student in students:
                    attendance_pct = student.get_attendance_percentage()
                    past_cgpa = student.cgpa or 0.0
                    grades = Grade.query.filter_by(student_id=student.id).all()
                    avg_internal = sum(g.internal_marks for g in grades if g.internal_marks) / len(grades) if grades else 0

                    result = predictor.predict(attendance_pct, past_cgpa, avg_internal)

                    all_predictions.append({
                        'student': student,
                        'attendance_pct': attendance_pct,
                        'past_cgpa': past_cgpa,
                        'risk_level': result['risk_level'],
                        'confidence': round(result['confidence'] * 100, 1),
                        'category': result['category']
                    })

                    # Save prediction
                    pred = Prediction(
                        prediction_type='performance',
                        student_id=student.id,
                        department=student.department,
                        predicted_value=float(result['category']),
                        confidence=result['confidence'],
                        parameters=json.dumps({
                            'attendance_pct': attendance_pct,
                            'past_cgpa': past_cgpa,
                            'avg_internal': round(avg_internal, 1)
                        })
                    )
                    db.session.add(pred)

                db.session.commit()
                flash(f'Bulk predictions generated for {len(all_predictions)} students.', 'success')

        except Exception as e:
            error_message = str(e)
            flash(f'Prediction error: {error_message}', 'danger')

    # Get at-risk students from recent predictions
    at_risk = Prediction.query.filter_by(prediction_type='performance', predicted_value=0).all()
    at_risk_students = []
    for pred in at_risk:
        if pred.student:
            at_risk_students.append(pred.student)
    at_risk_students = list(set(at_risk_students))  # Remove duplicates

    return render_template('predictions/performance.html',
                           students=students,
                           prediction_result=prediction_result,
                           all_predictions=all_predictions,
                           at_risk_students=at_risk_students,
                           error_message=error_message)


def _train_performance_model(predictor):
    """Train performance model from existing student data."""
    students = Student.query.filter_by(status='active').all()
    training_data = []

    for student in students:
        attendance_pct = student.get_attendance_percentage()
        past_cgpa = student.cgpa or 0.0
        grades = Grade.query.filter_by(student_id=student.id).all()
        avg_internal = sum(g.internal_marks for g in grades if g.internal_marks) / len(grades) if grades else 0

        # Determine category based on CGPA
        if past_cgpa >= 8.0:
            category = 3  # Excellent
        elif past_cgpa >= 6.0:
            category = 2  # Good
        elif past_cgpa >= 4.0:
            category = 1  # Average
        else:
            category = 0  # At Risk

        training_data.append({
            'attendance_pct': attendance_pct,
            'past_cgpa': past_cgpa,
            'internal_marks': avg_internal,
            'category': category
        })

    if len(training_data) >= 10:
        predictor.train(training_data)


@predictions_bp.route('/predictions/results')
@login_required
def prediction_results():
    """View all prediction history."""
    pred_type = request.args.get('type', '')

    query = Prediction.query

    if pred_type:
        query = query.filter_by(prediction_type=pred_type)

    predictions = query.order_by(Prediction.created_at.desc()).limit(100).all()

    return render_template('predictions/results.html', predictions=predictions, selected_type=pred_type)
