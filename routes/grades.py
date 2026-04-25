"""
Grade management routes — manage, view, report.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.grade import Grade
from models.student import Student
from models.course import Course

grades_bp = Blueprint('grades', __name__)


@grades_bp.route('/grades/manage', methods=['GET', 'POST'])
@login_required
def manage_grades():
    """Enter or update grades for a course."""
    if not (current_user.is_admin() or current_user.is_faculty()):
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))

    courses = Course.query.filter_by(college_id=current_user.college_id).order_by(Course.name).all()

    if request.method == 'POST':
        course_id = request.form.get('course_id')
        if not course_id:
            flash('Please select a course.', 'danger')
            return render_template('grades/manage.html', courses=courses)

        course = Course.query.filter_by(id=int(course_id), college_id=current_user.college_id).first()
        if not course:
            flash('Course not found.', 'danger')
            return render_template('grades/manage.html', courses=courses)

        students = Student.query.filter_by(
            department=course.department,
            semester=course.semester,
            status='active',
            college_id=current_user.college_id
        ).order_by(Student.name).all()

        try:
            for student in students:
                internal = request.form.get(f'internal_{student.id}', '')
                external = request.form.get(f'external_{student.id}', '')

                if internal and external:
                    internal_marks = float(internal)
                    external_marks = float(external)

                    # Find existing or create new
                    grade = Grade.query.filter_by(
                        student_id=student.id,
                        course_id=course.id
                    ).first()

                    if not grade:
                        grade = Grade(
                            student_id=student.id,
                            course_id=course.id,
                            semester=course.semester
                        )
                        db.session.add(grade)

                    grade.internal_marks = internal_marks
                    grade.external_marks = external_marks
                    grade.calculate_grade()

            db.session.commit()

            # Update CGPA for all affected students
            for student in students:
                _update_student_cgpa(student)

            db.session.commit()
            flash(f'Grades updated for {course.name}.', 'success')
            return redirect(url_for('grades.manage_grades'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating grades: {str(e)}', 'danger')

    # If GET with course_id, show students for grading
    selected_course_id = request.args.get('course_id', '')
    students = []
    existing_grades = {}

    if selected_course_id:
        course = Course.query.filter_by(id=int(selected_course_id), college_id=current_user.college_id).first()
        if course:
            students = Student.query.filter_by(
                department=course.department,
                semester=course.semester,
                status='active',
                college_id=current_user.college_id
            ).order_by(Student.name).all()

            for grade in Grade.query.filter_by(course_id=course.id).all():
                existing_grades[grade.student_id] = grade

    return render_template('grades/manage.html',
                           courses=courses,
                           students=students,
                           selected_course_id=selected_course_id,
                           existing_grades=existing_grades)


def _update_student_cgpa(student):
    """Recalculate CGPA for a student based on all grades."""
    grades = Grade.query.filter_by(student_id=student.id).all()
    if not grades:
        student.cgpa = 0.0
        return

    total_credit_points = 0
    total_credits = 0
    for grade in grades:
        course = Course.query.get(grade.course_id)
        if course:
            total_credit_points += grade.grade_point * course.credits
            total_credits += course.credits

    student.cgpa = round(total_credit_points / total_credits, 2) if total_credits > 0 else 0.0


@grades_bp.route('/grades/view/<int:student_id>')
@login_required
def view_grades(student_id):
    """View grades for a specific student."""
    student = Student.query.filter_by(id=student_id, college_id=current_user.college_id).first_or_404()

    # Access control for students
    if current_user.is_student():
        own_student = Student.query.filter_by(user_id=current_user.id).first()
        if not own_student or own_student.id != student_id:
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard.index'))

    grades = Grade.query.filter_by(student_id=student.id).all()

    # Group grades by semester
    semester_grades = {}
    for grade in grades:
        sem = grade.semester
        if sem not in semester_grades:
            semester_grades[sem] = []
        semester_grades[sem].append(grade)

    return render_template('grades/view.html',
                           student=student,
                           semester_grades=semester_grades)


@grades_bp.route('/grades/report')
@login_required
def grade_report():
    """Grade report with department-wise distribution."""
    if not (current_user.is_admin() or current_user.is_faculty()):
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard.index'))

    departments = Student.DEPARTMENTS
    selected_dept = request.args.get('department', '')

    report_data = []
    grade_dist = {'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C+': 0, 'C': 0, 'D': 0, 'F': 0}

    if selected_dept:
        students = Student.query.filter_by(department=selected_dept, status='active', college_id=current_user.college_id).order_by(Student.name).all()
        for student in students:
            grades = Grade.query.filter_by(student_id=student.id).all()
            for g in grades:
                if g.grade in grade_dist:
                    grade_dist[g.grade] += 1
            report_data.append({
                'student': student,
                'total_grades': len(grades),
                'cgpa': student.cgpa
            })
    else:
        # Overall distribution
        all_grades = db.session.query(Grade).join(Student).filter(Student.college_id == current_user.college_id).all()
        for g in all_grades:
            if g.grade in grade_dist:
                grade_dist[g.grade] += 1

    return render_template('grades/report.html',
                           departments=departments,
                           report_data=report_data,
                           grade_dist=grade_dist,
                           selected_dept=selected_dept)
