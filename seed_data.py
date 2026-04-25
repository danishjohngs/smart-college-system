"""
Seed Data Script for Smart College Management System
Populates the database with realistic sample data for testing and ML training.

Run: python seed_data.py
"""
import os
import sys
import random
from datetime import datetime, date, timedelta

# Ensure we can import from the project
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from extensions import db
from models.college import College
from models.user import User
from models.student import Student
from models.faculty import Faculty
from models.course import Course
from models.attendance import Attendance
from models.grade import Grade
from models.admission import AdmissionRecord

app = create_app()

# ============================================================
# Data Constants
# ============================================================
DEPARTMENTS = ['Computer Science', 'Electronics', 'Mechanical', 'Electrical', 'Civil']

MALE_FIRST_NAMES = [
    'Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Reyansh', 'Ayaan',
    'Krishna', 'Ishaan', 'Shaurya', 'Atharva', 'Advait', 'Dhruv', 'Kabir',
    'Ritvik', 'Aarush', 'Kayaan', 'Darsh', 'Veer', 'Rohan', 'Karthik',
    'Pranav', 'Rahul', 'Akash', 'Nikhil', 'Suresh', 'Gopal', 'Anand',
    'Manoj', 'Deepak', 'Rajesh', 'Vikram', 'Sanjay', 'Harsh', 'Dev'
]

FEMALE_FIRST_NAMES = [
    'Ananya', 'Diya', 'Saanvi', 'Aanya', 'Aadhya', 'Aarohi', 'Myra',
    'Sara', 'Kiara', 'Anika', 'Prisha', 'Riya', 'Isha', 'Navya',
    'Kavya', 'Shreya', 'Meera', 'Pooja', 'Neha', 'Divya', 'Sneha',
    'Priya', 'Anjali', 'Lakshmi', 'Swati', 'Rina', 'Tara', 'Jaya'
]

LAST_NAMES = [
    'Sharma', 'Verma', 'Gupta', 'Singh', 'Kumar', 'Patel', 'Reddy',
    'Nair', 'Pillai', 'Menon', 'Iyer', 'Joshi', 'Desai', 'Shah',
    'Mehta', 'Chauhan', 'Rao', 'Mishra', 'Pandey', 'Dubey', 'Thakur',
    'Das', 'Bose', 'Chatterjee', 'Mukherjee', 'Banerjee', 'Sen', 'Dey',
    'Thomas', 'Joseph', 'George', 'Mathew', 'John', 'Abraham', 'Philip'
]

FACULTY_NAMES = [
    ('Dr. Ramesh', 'Kumar'), ('Dr. Sunita', 'Sharma'), ('Prof. Anil', 'Verma'),
    ('Dr. Priya', 'Nair'), ('Prof. Suresh', 'Patel'), ('Dr. Kavitha', 'Reddy'),
    ('Prof. Rajesh', 'Gupta'), ('Dr. Meena', 'Iyer'), ('Prof. Vikram', 'Singh'),
    ('Dr. Lakshmi', 'Menon'), ('Prof. Gopal', 'Joshi'), ('Dr. Deepa', 'Rao'),
    ('Dr. Arindam', 'Bose'), ('Prof. Shweta', 'Mishra'), ('Dr. Rahul', 'Sen'),
    ('Prof. Ananya', 'Desai'), ('Dr. Harish', 'Thakur'), ('Prof. Sneha', 'Dey'),
    ('Dr. Ajay', 'Chatterjee'), ('Prof. Divya', 'Pillai')
]

DESIGNATIONS = [
    'Assistant Professor', 'Associate Professor', 'Professor',
    'Senior Lecturer', 'Head of Department'
]

QUALIFICATIONS = [
    'Ph.D. in Computer Science', 'M.Tech in Electronics', 'Ph.D. in Mechanical Engineering',
    'M.Tech in Electrical Engineering', 'Ph.D. in Civil Engineering',
    'M.Sc. in Mathematics', 'Ph.D. in Physics', 'M.Tech in Information Technology',
    'Ph.D. in Data Science', 'M.Tech in VLSI Design', 'Ph.D. in Structural Engineering',
    'M.Tech in Power Systems'
]

# Course data: (code, name, department, semester, credits)
COURSES_DATA = [
    ('CS101', 'Introduction to Programming', 'Computer Science', 1, 4),
    ('CS201', 'Data Structures', 'Computer Science', 3, 4),
    ('CS301', 'Database Management Systems', 'Computer Science', 3, 3),
    ('CS401', 'Operating Systems', 'Computer Science', 5, 4),
    ('CS501', 'Machine Learning', 'Computer Science', 5, 3),
    ('EC101', 'Basic Electronics', 'Electronics', 1, 4),
    ('EC201', 'Digital Circuits', 'Electronics', 3, 3),
    ('EC301', 'Microprocessors', 'Electronics', 5, 4),
    ('ME101', 'Engineering Mechanics', 'Mechanical', 1, 4),
    ('ME201', 'Thermodynamics', 'Mechanical', 3, 3),
    ('ME301', 'Fluid Mechanics', 'Mechanical', 5, 4),
    ('EE101', 'Circuit Theory', 'Electrical', 1, 4),
    ('EE201', 'Electromagnetic Theory', 'Electrical', 3, 3),
    ('EE301', 'Power Electronics', 'Electrical', 5, 4),
    ('CE101', 'Surveying', 'Civil', 1, 3),
    ('CE201', 'Structural Analysis', 'Civil', 3, 4),
    ('CE301', 'Geotechnical Engineering', 'Civil', 5, 3),
]

ADDRESSES = [
    'No. 12, MG Road, Kochi, Kerala',
    '45/A, Anna Nagar, Chennai, Tamil Nadu',
    'Plot 78, Banjara Hills, Hyderabad, Telangana',
    '23, Koramangala, Bangalore, Karnataka',
    'House 34, Sector 15, Chandigarh',
    '67, Civil Lines, Jaipur, Rajasthan',
    '89/B, Salt Lake, Kolkata, West Bengal',
    '12, Aundh Road, Pune, Maharashtra',
    '56, Model Town, Lucknow, Uttar Pradesh',
    '78, Jubilee Hills, Hyderabad, Telangana',
    '34/C, Indiranagar, Bangalore, Karnataka',
    '90, Adyar, Chennai, Tamil Nadu',
    'Flat 4B, Marine Drive, Kochi, Kerala',
    '15, Gomti Nagar, Lucknow, Uttar Pradesh',
    '22, Alwarpet, Chennai, Tamil Nadu',
]


def seed():
    """Main seed function."""
    with app.app_context():
        print("=" * 60)
        print("  Smart College Management System — Seed Data")
        print("=" * 60)

        # Drop and recreate all tables
        print("\n[1/8] Resetting database...")
        db.drop_all()
        db.create_all()
        print("  OK Database tables created.")

        # --- ADMIN USER & DEMO COLLEGE ---
        print("\n[1.5/8] Creating Admin User and Demo College...")
        # Create admin user first (no college assigned yet)
        admin_user = User(
            username='admin',
            email='smartcollegeai@gmail.com',
            role='admin',
            status='approved',
            full_name='System Admin'
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()

        # Create Demo College authored by admin
        college = College(name='Demo College', location='Virtual', college_code='DEMO123', created_by=admin_user.id)
        db.session.add(college)
        db.session.commit()

        # Assign college to admin
        admin_user.college_id = college.id
        db.session.commit()
        print(f"  OK Demo college created with code: {college.college_code}")

        # --- USERS ---
        print("\n[2/8] Creating users...")
        users = create_users(college.id)
        print(f"  OK {len(users)} users created.")

        # --- FACULTY ---
        print("\n[3/8] Creating faculty...")
        faculty_list = create_faculty(users, college.id)
        print(f"  OK {len(faculty_list)} faculty members created.")

        # --- STUDENTS ---
        print("\n[4/8] Creating students...")
        student_list = create_students(users, college.id)
        print(f"  OK {len(student_list)} students created.")

        # --- COURSES ---
        print("\n[5/8] Creating courses...")
        course_list = create_courses(faculty_list, college.id)
        print(f"  OK {len(course_list)} courses created.")

        # --- ATTENDANCE ---
        print("\n[6/8] Creating attendance records...")
        att_count = create_attendance(student_list, course_list, faculty_list)
        print(f"  OK {att_count} attendance records created.")

        # --- GRADES ---
        print("\n[7/8] Creating grade records...")
        grade_count = create_grades(student_list, course_list)
        print(f"  OK {grade_count} grade records created.")

        # --- ADMISSION RECORDS ---
        print("\n[8/8] Creating admission history (10 years)...")
        adm_count = create_admission_records(college.id)
        print(f"  OK {adm_count} admission records created.")

        # --- TRAIN ML MODELS ---
        print("\n" + "=" * 60)
        print("  Training ML Models...")
        print("=" * 60)
        train_models(college.id)

        print("\n" + "=" * 60)
        print("  Seed data complete!")
        print("=" * 60)
        print("\n  Run: python app.py")
        print("  Open: http://localhost:5000")
        print("  Credentials are in seed_data.py (developer reference only)")
        print("=" * 60)


def create_users(college_id):
    """Create admin, faculty, and student user accounts."""
    users = []

    # Admin user is now created via the /setup page


    # Faculty users
    for i in range(len(FACULTY_NAMES)):
        fname = FACULTY_NAMES[i][0].replace('Dr. ', '').replace('Prof. ', '').lower()
        lname = FACULTY_NAMES[i][1].lower()
        username = f'{fname}.{lname}'
        dept = DEPARTMENTS[i % len(DEPARTMENTS)]
        user = User(
            username=username,
            email=f'{username}.demo@localhost',
            role='faculty',
            status='approved',
            full_name=f'{FACULTY_NAMES[i][0]} {FACULTY_NAMES[i][1]}',
            department=dept,
            college_id=college_id
        )
        user.set_password('faculty123')
        db.session.add(user)
        users.append(('faculty', user))

    # Student users
    for i in range(50):
        gender = random.choice(['Male', 'Female'])
        if gender == 'Male':
            fname = random.choice(MALE_FIRST_NAMES).lower()
        else:
            fname = random.choice(FEMALE_FIRST_NAMES).lower()
        lname = random.choice(LAST_NAMES).lower()
        username = f'{fname}.{lname}{random.randint(1, 99)}'

        # Ensure unique username
        while User.query.filter_by(username=username).first():
            username = f'{fname}.{lname}{random.randint(1, 999)}'

        user = User(
            username=username,
            email=f'{username}.demo@localhost',
            role='student',
            status='approved',
            full_name=f'{fname.capitalize()} {lname.capitalize()}',
            college_id=college_id
        )
        user.set_password('student123')
        db.session.add(user)
        users.append(('student', user))

    db.session.commit()

    # --- Sample pending/rejected users for demo ---
    pending_users_data = [
        User(full_name='Vikram Desai', username='vikram.desai', email='vikram@test.com',
             role='student', department='Computer Science', id_proof_number='CS2026099',
             phone='9876500001', status='pending', college_id=college_id),
        User(full_name='Sneha Kapoor', username='sneha.kapoor', email='sneha@test.com',
             role='faculty', department='Electronics', id_proof_number='FAC2026005',
             phone='9876500002', status='pending', college_id=college_id),
        User(full_name='Rejected User', username='rejected.user', email='rejected@test.com',
             role='student', department='Mechanical', id_proof_number='ME2026050',
             phone='9876500003', status='rejected', rejection_reason='Invalid college ID provided', college_id=college_id),
    ]
    for u in pending_users_data:
        u.set_password('test123')
        db.session.add(u)

    db.session.commit()
    return users


def create_faculty(users, college_id):
    """Create faculty records linked to user accounts."""
    faculty_list = []
    faculty_users = [u for r, u in users if r == 'faculty']

    for i, (first, last) in enumerate(FACULTY_NAMES):
        name = f'{first} {last}'
        dept = DEPARTMENTS[i % len(DEPARTMENTS)]
        user_id = faculty_users[i].id if i < len(faculty_users) else None

        fac = Faculty(
            user_id=user_id,
            name=name,
            employee_id=f'FAC{2020 + i:04d}',
            email=f'{first.split()[-1].lower()}.{last.lower()}.demo@localhost',
            phone=f'+91 {random.randint(7000000000, 9999999999)}',
            department=dept,
            designation=random.choice(DESIGNATIONS),
            qualification=QUALIFICATIONS[i % len(QUALIFICATIONS)],
            college_id=college_id
        )
        db.session.add(fac)
        faculty_list.append(fac)

    db.session.commit()
    return faculty_list


def create_students(users, college_id):
    """Create 55 student records with realistic data."""
    student_list = []
    student_users = [u for r, u in users if r == 'student']
    student_user_idx = 0

    for i in range(100):
        gender = random.choice(['Male', 'Female'])
        if gender == 'Male':
            first_name = random.choice(MALE_FIRST_NAMES)
        else:
            first_name = random.choice(FEMALE_FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        name = f'{first_name} {last_name}'

        dept = DEPARTMENTS[i % len(DEPARTMENTS)]
        semester = random.choice([1, 3, 5])
        admission_year = 2026 - (semester // 2) - 1

        # Link first 20 students to user accounts
        user_id = None
        if student_user_idx < len(student_users):
            user_id = student_users[student_user_idx].id
            student_user_idx += 1

        dob = date(random.randint(2001, 2005), random.randint(1, 12), random.randint(1, 28))

        student = Student(
            user_id=user_id,
            name=name,
            roll_number=f'{dept[:2].upper()}{admission_year}{i + 1:03d}',
            email=f'{first_name.lower()}.{last_name.lower()}{i}.demo@localhost',
            phone=f'+91 {random.randint(7000000000, 9999999999)}',
            department=dept,
            semester=semester,
            admission_year=admission_year,
            date_of_birth=dob,
            gender=gender,
            address=random.choice(ADDRESSES),
            cgpa=0.0,
            status='active',
            college_id=college_id
        )
        db.session.add(student)
        student_list.append(student)

    db.session.commit()
    return student_list


def create_courses(faculty_list, college_id):
    """Create courses and assign faculty."""
    course_list = []

    for code, name, dept, semester, credits in COURSES_DATA:
        # Assign faculty from same department
        dept_faculty = [f for f in faculty_list if f.department == dept]
        faculty_id = random.choice(dept_faculty).id if dept_faculty else faculty_list[0].id

        course = Course(
            code=code,
            name=name,
            department=dept,
            semester=semester,
            credits=credits,
            faculty_id=faculty_id,
            college_id=college_id
        )
        db.session.add(course)
        course_list.append(course)

    db.session.commit()
    return course_list


def create_attendance(student_list, course_list, faculty_list):
    """Create 600+ attendance records spread across dates."""
    count = 0
    today = date.today()

    for course in course_list:
        # Students in this course
        students = [s for s in student_list
                     if s.department == course.department and s.semester == course.semester]

        if not students:
            continue

        # Faculty who could mark
        dept_faculty = [f for f in faculty_list if f.department == course.department]
        marker = dept_faculty[0] if dept_faculty else faculty_list[0]

        # Create attendance for 15-20 days
        num_days = random.randint(15, 20)
        for day_offset in range(num_days):
            att_date = today - timedelta(days=day_offset + 1)
            if att_date.weekday() >= 5:  # Skip weekends
                continue

            for student in students:
                # 80% present, 10% absent, 10% late
                r = random.random()
                if r < 0.80:
                    status = 'present'
                elif r < 0.90:
                    status = 'absent'
                else:
                    status = 'late'

                att = Attendance(
                    student_id=student.id,
                    course_id=course.id,
                    date=att_date,
                    status=status,
                    marked_by=marker.id
                )
                db.session.add(att)
                count += 1

    db.session.commit()
    return count


def create_grades(student_list, course_list):
    """Create grade records and calculate CGPA for students."""
    count = 0

    for course in course_list:
        students = [s for s in student_list
                     if s.department == course.department and s.semester == course.semester]

        for student in students:
            # Generate realistic marks
            performance_level = random.choice(['excellent', 'good', 'average', 'poor'])

            if performance_level == 'excellent':
                internal = random.uniform(40, 50)
                external = random.uniform(40, 50)
            elif performance_level == 'good':
                internal = random.uniform(30, 42)
                external = random.uniform(30, 42)
            elif performance_level == 'average':
                internal = random.uniform(20, 35)
                external = random.uniform(20, 35)
            else:
                internal = random.uniform(5, 25)
                external = random.uniform(5, 25)

            internal = round(internal, 1)
            external = round(external, 1)

            grade_obj = Grade(
                student_id=student.id,
                course_id=course.id,
                semester=course.semester,
                internal_marks=internal,
                external_marks=external
            )
            grade_obj.calculate_grade()
            db.session.add(grade_obj)
            count += 1

    db.session.commit()

    # Calculate CGPA for all students
    for student in student_list:
        grades = Grade.query.filter_by(student_id=student.id).all()
        if not grades:
            continue

        total_cp = 0
        total_credits = 0
        for g in grades:
            c = Course.query.get(g.course_id)
            if c:
                total_cp += g.grade_point * c.credits
                total_credits += c.credits

        student.cgpa = round(total_cp / total_credits, 2) if total_credits > 0 else 0.0

    db.session.commit()
    return count


def create_admission_records(college_id):
    """Create 10 years of admission history for AI training."""
    count = 0

    for year in range(2016, 2026):
        for dept in DEPARTMENTS:
            # Simulate growth trends
            base_applications = random.randint(100, 200)
            growth = (year - 2016) * random.randint(3, 8)
            applications = base_applications + growth

            # Capacity increases slowly
            capacity = 60 + ((year - 2016) // 3) * 10

            # Admission rate varies
            admission_rate = random.uniform(0.35, 0.65)
            admitted = min(int(applications * admission_rate), capacity)

            record = AdmissionRecord(
                year=year,
                department=dept,
                applications_received=applications,
                students_admitted=admitted,
                total_capacity=capacity,
                college_id=college_id
            )
            db.session.add(record)
            count += 1

    db.session.commit()
    return count


def train_models(college_id):
    """Train ML models after seeding data."""
    try:
        from ml.admission_predictor import AdmissionPredictor
        from ml.performance_predictor import PerformancePredictor

        # Train Admission Model
        print("\n  [ML 1/2] Training Admission Predictor...")
        records = AdmissionRecord.query.all()
        training_data = [{
            'year': r.year,
            'department': r.department,
            'applications': r.applications_received,
            'admitted': r.students_admitted
        } for r in records]

        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml', 'saved_models', f'admission_model_{college_id}.pkl')
        encoder_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml', 'saved_models', f'admission_encoder_{college_id}.pkl')
        predictor = AdmissionPredictor(model_path=model_path, encoder_path=encoder_path)
        score = predictor.train(training_data)
        print(f"    ✓ R² Score: {score:.4f} ({len(training_data)} samples)")

        # Train Performance Model
        print("  [ML 2/2] Training Performance Predictor...")
        students = Student.query.all()
        perf_data = []
        for student in students:
            att_pct = student.get_attendance_percentage()
            cgpa = student.cgpa or 0.0
            grades = Grade.query.filter_by(student_id=student.id).all()
            avg_internal = sum(g.internal_marks for g in grades if g.internal_marks) / len(grades) if grades else 0

            if cgpa >= 8.0:
                cat = 3
            elif cgpa >= 6.0:
                cat = 2
            elif cgpa >= 4.0:
                cat = 1
            else:
                cat = 0

            perf_data.append({
                'attendance_pct': att_pct,
                'past_cgpa': cgpa,
                'internal_marks': avg_internal,
                'category': cat
            })

        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml', 'saved_models', f'performance_model_{college_id}.pkl')
        predictor2 = PerformancePredictor(model_path=model_path)
        accuracy = predictor2.train(perf_data)
        print(f"    ✓ Accuracy: {accuracy:.4f} ({len(perf_data)} samples)")

    except Exception as e:
        print(f"    ⚠ ML training error: {e}")
        print("    Models can be trained later using: python -c \"from ml.train_models import train_all; train_all()\"")


if __name__ == '__main__':
    seed()
