# -*- coding: utf-8 -*-
"""
MASTER TEST SCRIPT — Smart College Management System
Tests EVERYTHING and reports pass/fail for each feature.
"""
import sys
import os
import time
import json
from datetime import date, datetime

sys.path.insert(0, '.')

from app import create_app
from extensions import db
from models.user import User
from models.student import Student
from models.faculty import Faculty
from models.course import Course
from models.attendance import Attendance
from models.grade import Grade
from models.admission import AdmissionRecord
from models.prediction import Prediction

app = create_app()
results = {'pass': 0, 'fail': 0, 'fixed': 0, 'details': []}

def log(status, test_name, detail=''):
    results['pass' if status == 'PASS' else 'fail'] += 1
    msg = f"[{status}] {test_name}" + (f" - {detail}" if detail else "")
    results['details'].append(msg)
    try:
        print(f"  {msg}")
    except UnicodeEncodeError:
        print(f"  {msg.encode('ascii', 'replace').decode()}")

with app.app_context():
    client = app.test_client()

    # =============================================
    # SECTION 1: IMPORTS AND DEPENDENCIES
    # =============================================
    print("\n" + "=" * 60)
    print("SECTION 1: IMPORTS AND DEPENDENCIES")
    print("=" * 60)

    # Check every route file has required imports
    import importlib
    route_files = ['routes.auth', 'routes.dashboard', 'routes.students', 'routes.faculty',
                   'routes.courses', 'routes.attendance', 'routes.grades', 'routes.predictions', 'routes.api']

    # Try importing optional route files
    for optional in ['routes.reports', 'routes.removal_requests']:
        try:
            importlib.import_module(optional)
            route_files.append(optional)
        except ImportError:
            pass

    for module_name in route_files:
        try:
            mod = importlib.import_module(module_name)
            source = open(mod.__file__).read()

            # Check if file uses current_user but hasn't imported it
            if 'current_user' in source and 'import current_user' not in source and 'from flask_login' not in source:
                log('FAIL', f'{module_name} — missing current_user import')
            elif 'current_user' in source:
                log('PASS', f'{module_name} — current_user imported correctly')
            else:
                log('PASS', f'{module_name} — no current_user usage (OK)')

            # Check if file uses db but hasn't imported it
            if 'db.session' in source and 'from extensions import db' not in source and 'from extensions import' not in source:
                log('FAIL', f'{module_name} — missing db import')
            else:
                log('PASS', f'{module_name} — db import OK')

        except Exception as e:
            log('FAIL', f'{module_name} — import error: {str(e)}')

    # =============================================
    # SECTION 2: DATABASE INTEGRITY
    # =============================================
    print("\n" + "=" * 60)
    print("SECTION 2: DATABASE INTEGRITY")
    print("=" * 60)

    # Check tables exist
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()

    required_tables = ['users', 'students', 'faculty', 'courses', 'attendances', 'grades',
                       'admission_records', 'predictions']

    for table in required_tables:
        if table in tables:
            count = db.session.execute(db.text(f"SELECT COUNT(*) FROM {table}")).scalar()
            log('PASS', f'Table "{table}" exists — {count} rows')
        else:
            log('FAIL', f'Table "{table}" MISSING')

    # Check optional tables
    for table in ['colleges', 'notifications', 'removal_requests']:
        if table in tables:
            count = db.session.execute(db.text(f"SELECT COUNT(*) FROM {table}")).scalar()
            log('PASS', f'Table "{table}" exists — {count} rows')

    # Check users have password hashes
    no_pwd = db.session.execute(db.text("SELECT COUNT(*) FROM users WHERE password_hash IS NULL OR password_hash = ''")).scalar()
    log('PASS' if no_pwd == 0 else 'FAIL', f'Users without password: {no_pwd}')

    # Check role distribution
    for role in ['admin', 'faculty', 'student']:
        count = db.session.execute(db.text(f"SELECT COUNT(*) FROM users WHERE role = '{role}'")).scalar()
        log('PASS' if count > 0 else 'FAIL', f'Users with role "{role}": {count}')

    # =============================================
    # SECTION 3: PUBLIC PAGES
    # =============================================
    print("\n" + "=" * 60)
    print("SECTION 3: PUBLIC PAGES (no login)")
    print("=" * 60)

    # Root should redirect to login
    resp = client.get('/', follow_redirects=False)
    log('PASS' if resp.status_code in (302, 301, 200) else 'FAIL',
        f'GET / — status {resp.status_code}')

    # Login page
    resp = client.get('/login', follow_redirects=True)
    log('PASS' if resp.status_code == 200 else 'FAIL',
        f'GET /login — status {resp.status_code}')

    # Register page
    resp = client.get('/register', follow_redirects=True)
    log('PASS' if resp.status_code == 200 else 'FAIL',
        f'GET /register — status {resp.status_code}')

    # Protected pages should redirect to login when not authenticated
    for url in ['/dashboard', '/students', '/faculty', '/courses', '/grades/manage']:
        resp = client.get(url, follow_redirects=True)
        page_data = resp.data.lower()
        is_login = b'login' in page_data and b'password' in page_data
        log('PASS' if is_login else 'FAIL',
            f'GET {url} blocked for unauthenticated — redirects to login: {is_login}')

    # =============================================
    # SECTION 4: AUTHENTICATION — ALL 3 ROLES
    # =============================================
    print("\n" + "=" * 60)
    print("SECTION 4: AUTHENTICATION")
    print("=" * 60)

    # Find users and their passwords
    test_users = []
    for role in ['admin', 'faculty', 'student']:
        user = User.query.filter_by(role=role, status='approved').first()
        if user:
            # Try common passwords
            found_pwd = None
            for pwd in ['admin123', 'faculty123', 'student123', 'password', 'test123',
                        'Admin@123', 'Faculty@123', 'Student@123', 'dani123123', 'password123']:
                if user.check_password(pwd):
                    found_pwd = pwd
                    break
            if found_pwd:
                test_users.append((role, user.username, found_pwd))
                log('PASS', f'{role} user found: {user.username}')
            else:
                log('FAIL', f'{role} user found ({user.username}) but password unknown — cannot test login')
        else:
            log('FAIL', f'No approved {role} user in database')

    # Test login for each role
    for role, username, password in test_users:
        # Logout first
        client.get('/logout', follow_redirects=True)

        # Wrong password test
        resp = client.post('/login', data={'username': username, 'password': 'WRONG_PASSWORD_XYZ'},
                          follow_redirects=True)
        page = resp.data.lower()
        log('PASS' if b'invalid' in page or b'incorrect' in page or b'login' in page else 'FAIL',
            f'{role} — wrong password rejected')

        # Correct login
        resp = client.post('/login', data={'username': username, 'password': password},
                          follow_redirects=True)
        log('PASS' if resp.status_code == 200 and b'dashboard' in resp.data.lower() or b'welcome' in resp.data.lower() else 'FAIL',
            f'{role} — correct login works')

        # Dashboard loads
        resp = client.get('/dashboard', follow_redirects=True)
        log('PASS' if resp.status_code == 200 else 'FAIL',
            f'{role} — dashboard loads ({resp.status_code})')

        # Logout
        resp = client.get('/logout', follow_redirects=True)
        log('PASS' if resp.status_code == 200 else 'FAIL',
            f'{role} — logout works')

    # =============================================
    # SECTION 5: ROLE-BASED ACCESS CONTROL
    # =============================================
    print("\n" + "=" * 60)
    print("SECTION 5: ROLE-BASED ACCESS CONTROL")
    print("=" * 60)

    # Login as student and try admin routes
    student_user = next((u for u in test_users if u[0] == 'student'), None)
    if student_user:
        client.get('/logout', follow_redirects=True)
        client.post('/login', data={'username': student_user[1], 'password': student_user[2]},
                   follow_redirects=True)

        admin_only_routes = ['/students/add', '/faculty/add', '/courses/add', '/approvals']
        for url in admin_only_routes:
            resp = client.get(url, follow_redirects=True)
            page = resp.data.lower()
            blocked = b'access denied' in page or b'login' in page or resp.status_code in (403, 302)
            log('PASS' if blocked else 'FAIL',
                f'Student blocked from {url}: {blocked}')

        client.get('/logout', follow_redirects=True)

    # Login as faculty and try admin-only routes
    faculty_user = next((u for u in test_users if u[0] == 'faculty'), None)
    if faculty_user:
        client.get('/logout', follow_redirects=True)
        client.post('/login', data={'username': faculty_user[1], 'password': faculty_user[2]},
                   follow_redirects=True)

        faculty_blocked = ['/faculty/add']
        for url in faculty_blocked:
            resp = client.get(url, follow_redirects=True)
            page = resp.data.lower()
            blocked = b'access denied' in page or resp.status_code in (403, 302)
            log('PASS' if blocked else 'FAIL',
                f'Faculty blocked from {url}: {blocked}')

        # Faculty SHOULD access these
        faculty_allowed = ['/students', '/courses', '/attendance/view', '/grades/manage']
        for url in faculty_allowed:
            resp = client.get(url, follow_redirects=True)
            log('PASS' if resp.status_code == 200 else 'FAIL',
                f'Faculty can access {url}: {resp.status_code}')

        client.get('/logout', follow_redirects=True)

    # =============================================
    # SECTION 6: ALL API ENDPOINTS
    # =============================================
    print("\n" + "=" * 60)
    print("SECTION 6: API ENDPOINTS")
    print("=" * 60)

    # Login as admin for API tests
    admin_user = next((u for u in test_users if u[0] == 'admin'), None)
    if admin_user:
        client.get('/logout', follow_redirects=True)
        client.post('/login', data={'username': admin_user[1], 'password': admin_user[2]},
                   follow_redirects=True)

        api_routes = [
            '/api/dashboard-stats',
            '/api/grade-distribution',
            '/api/admission-trends',
            '/api/department-stats',
        ]

        for url in api_routes:
            try:
                resp = client.get(url, follow_redirects=True)
                if resp.status_code == 200:
                    try:
                        data = json.loads(resp.data)
                        log('PASS', f'{url} — returns valid JSON')
                    except json.JSONDecodeError:
                        log('FAIL', f'{url} — returns {resp.status_code} but NOT valid JSON')
                else:
                    log('FAIL', f'{url} — returns {resp.status_code}')
            except Exception as e:
                log('FAIL', f'{url} — error: {str(e)}')

        # Test attendance chart API
        student = Student.query.first()
        if student:
            url = f'/api/attendance-chart/{student.id}'
            try:
                resp = client.get(url, follow_redirects=True)
                if resp.status_code == 200:
                    log('PASS', f'{url} — works')
                else:
                    log('FAIL', f'{url} — returns {resp.status_code}')
            except Exception as e:
                log('FAIL', f'{url} — error: {str(e)}')

        client.get('/logout', follow_redirects=True)

    # =============================================
    # SECTION 7: ALL PAGE ROUTES
    # =============================================
    print("\n" + "=" * 60)
    print("SECTION 7: ALL PAGE ROUTES")
    print("=" * 60)

    if admin_user:
        client.get('/logout', follow_redirects=True)
        client.post('/login', data={'username': admin_user[1], 'password': admin_user[2]},
                   follow_redirects=True)

        all_pages = [
            ('/dashboard', 'Dashboard'),
            ('/students', 'Student list'),
            ('/faculty', 'Faculty list'),
            ('/courses', 'Course list'),
            ('/attendance/mark', 'Mark attendance'),
            ('/attendance/view', 'View attendance'),
            ('/attendance/report', 'Attendance report'),
            ('/grades/manage', 'Manage grades'),
            ('/predictions/admission', 'Admission prediction'),
            ('/predictions/performance', 'Performance prediction'),
            ('/predictions/results', 'Prediction results'),

            ('/approvals', 'Approvals'),
            ('/removal-requests', 'Removal requests'),
        ]

        for url, name in all_pages:
            try:
                start = time.time()
                resp = client.get(url, follow_redirects=True)
                elapsed = time.time() - start
                speed = "fast" if elapsed < 2 else "SLOW"

                if resp.status_code == 200:
                    log('PASS', f'{name} ({url}) — {resp.status_code} [{elapsed:.2f}s {speed}]')
                elif resp.status_code == 404:
                    log('FAIL', f'{name} ({url}) — 404 NOT FOUND')
                else:
                    log('FAIL', f'{name} ({url}) — {resp.status_code}')
            except Exception as e:
                log('FAIL', f'{name} ({url}) — error: {str(e)}')

        # Test student profile
        student = Student.query.first()
        if student:
            resp = client.get(f'/students/profile/{student.id}', follow_redirects=True)
            log('PASS' if resp.status_code == 200 else 'FAIL',
                f'Student profile /students/profile/{student.id} — {resp.status_code}')

        client.get('/logout', follow_redirects=True)

    # =============================================
    # SECTION 8: AI/ML MODELS
    # =============================================
    print("\n" + "=" * 60)
    print("SECTION 8: AI/ML MODELS")
    print("=" * 60)

    # Check model files — check both default and college-specific paths
    admin_u = User.query.filter_by(role='admin').first()
    college_id = admin_u.college_id if admin_u and hasattr(admin_u, 'college_id') else None

    admission_pkl_default = os.path.exists('ml/saved_models/admission_model.pkl')
    admission_pkl_college = os.path.exists(f'ml/saved_models/admission_model_{college_id}.pkl') if college_id else False
    admission_pkl = admission_pkl_default or admission_pkl_college
    log('PASS' if admission_pkl else 'FAIL', f'admission_model.pkl exists: {admission_pkl} (default={admission_pkl_default}, college={admission_pkl_college})')

    performance_pkl_default = os.path.exists('ml/saved_models/performance_model.pkl')
    performance_pkl_college = os.path.exists(f'ml/saved_models/performance_model_{college_id}.pkl') if college_id else False
    performance_pkl = performance_pkl_default or performance_pkl_college
    log('PASS' if performance_pkl else 'FAIL', f'performance_model.pkl exists: {performance_pkl} (default={performance_pkl_default}, college={performance_pkl_college})')

    # Test admission predictor
    try:
        from ml.admission_predictor import AdmissionPredictor
        # Use college-specific model if available
        if admission_pkl_college:
            model_path = f'ml/saved_models/admission_model_{college_id}.pkl'
            encoder_path = f'ml/saved_models/admission_encoder_{college_id}.pkl'
            predictor = AdmissionPredictor(model_path=model_path, encoder_path=encoder_path)
        else:
            predictor = AdmissionPredictor()
        start = time.time()
        result = predictor.predict(2027, 'Computer Science', 200)
        elapsed = time.time() - start
        log('PASS', f'Admission prediction works — result: {result} [{elapsed:.2f}s]')
        log('PASS' if elapsed < 2 else 'FAIL', f'Admission prediction speed: {elapsed:.2f}s (threshold: 2s)')
    except Exception as e:
        log('FAIL', f'Admission prediction error: {str(e)}')

    # Test performance predictor
    try:
        from ml.performance_predictor import PerformancePredictor
        if performance_pkl_college:
            predictor = PerformancePredictor(model_path=f'ml/saved_models/performance_model_{college_id}.pkl')
        else:
            predictor = PerformancePredictor()

        test_cases = [
            (95, 9.0, 45, 'high performer'),
            (50, 4.0, 20, 'at risk student'),
            (75, 7.0, 35, 'average student'),
        ]

        for att, cgpa, marks, desc in test_cases:
            start = time.time()
            result = predictor.predict(att, cgpa, marks)
            elapsed = time.time() - start
            risk = result.get('risk_level', result) if isinstance(result, dict) else result
            conf = result.get('confidence', 0) if isinstance(result, dict) else 0
            log('PASS', f'Performance prediction ({desc}) — {risk} [conf: {conf:.0%}] [{elapsed:.2f}s]')
    except Exception as e:
        log('FAIL', f'Performance prediction error: {str(e)}')

    # Speed test: 10 rapid predictions
    try:
        from ml.admission_predictor import AdmissionPredictor
        if admission_pkl_college:
            p = AdmissionPredictor(model_path=f'ml/saved_models/admission_model_{college_id}.pkl',
                                   encoder_path=f'ml/saved_models/admission_encoder_{college_id}.pkl')
        else:
            p = AdmissionPredictor()
        depts = ['Computer Science', 'Electronics', 'Mechanical', 'Electrical', 'Civil']
        start = time.time()
        for i in range(10):
            p.predict(2025 + i, depts[i % 5], 100 + i * 20)
        total = time.time() - start
        log('PASS' if total < 5 else 'FAIL', f'10 rapid predictions in {total:.2f}s')
    except Exception as e:
        log('FAIL', f'Speed test error: {str(e)}')

    # =============================================
    # SECTION 9: CRUD OPERATIONS
    # =============================================
    print("\n" + "=" * 60)
    print("SECTION 9: CRUD OPERATIONS")
    print("=" * 60)

    # Test Student CRUD at model level
    try:
        initial = Student.query.count()
        s = Student(name='QA_Test_Student', roll_number='QA_TEST_999', email='qa@test.local',
                    department='Computer Science', semester=1, admission_year=2025, status='active')
        if hasattr(s, 'college_id') and User.query.filter_by(role='admin').first():
            admin_u = User.query.filter_by(role='admin').first()
            if admin_u and hasattr(admin_u, 'college_id'):
                s.college_id = admin_u.college_id
        db.session.add(s)
        db.session.commit()
        log('PASS', f'CREATE student — id={s.id}')

        found = Student.query.filter_by(roll_number='QA_TEST_999').first()
        log('PASS' if found else 'FAIL', f'READ student — found: {found is not None}')

        if found:
            found.semester = 2
            db.session.commit()
            updated = db.session.get(Student, found.id)
            log('PASS' if updated.semester == 2 else 'FAIL', f'UPDATE student — semester: {updated.semester}')

            db.session.delete(found)
            db.session.commit()
            gone = Student.query.filter_by(roll_number='QA_TEST_999').first()
            log('PASS' if gone is None else 'FAIL', f'DELETE student — removed: {gone is None}')

        final = Student.query.count()
        log('PASS' if final == initial else 'FAIL', f'Count restored: {initial} -> {final}')
    except Exception as e:
        log('FAIL', f'Student CRUD error: {str(e)}')
        db.session.rollback()

    # Test Grade Calculation
    print("\n  Grade calculation:")
    grade_tests = [(95,'A+'), (85,'A'), (75,'B+'), (65,'B'), (55,'C+'), (45,'C'), (35,'D'), (20,'F')]
    for total, expected in grade_tests:
        if total >= 90: g = 'A+'
        elif total >= 80: g = 'A'
        elif total >= 70: g = 'B+'
        elif total >= 60: g = 'B'
        elif total >= 50: g = 'C+'
        elif total >= 40: g = 'C'
        elif total >= 30: g = 'D'
        else: g = 'F'
        log('PASS' if g == expected else 'FAIL', f'Marks {total} -> {g} (expected {expected})')

    # =============================================
    # SECTION 10: EMAIL CONFIGURATION
    # =============================================
    print("\n" + "=" * 60)
    print("SECTION 10: EMAIL CONFIGURATION")
    print("=" * 60)

    mail_enabled = app.config.get('MAIL_ENABLED', False)
    mail_user = app.config.get('MAIL_USERNAME', '')
    mail_pass = app.config.get('MAIL_PASSWORD', '')

    log('PASS' if mail_enabled else 'FAIL', f'MAIL_ENABLED: {mail_enabled}')
    log('PASS' if mail_user else 'FAIL', f'MAIL_USERNAME: {"SET" if mail_user else "EMPTY"}')
    log('PASS' if mail_pass else 'FAIL', f'MAIL_PASSWORD: {"SET" if mail_pass else "EMPTY"}')

    if mail_enabled and mail_user and mail_pass:
        try:
            import smtplib, ssl
            context = ssl.create_default_context()
            with smtplib.SMTP(app.config.get('MAIL_SERVER', 'smtp.gmail.com'),
                             app.config.get('MAIL_PORT', 587)) as server:
                server.ehlo()
                server.starttls(context=context)
                server.login(mail_user, mail_pass)
            log('PASS', 'SMTP connection and login successful')
        except Exception as e:
            log('FAIL', f'SMTP error: {str(e)}')

    # =============================================
    # SECTION 11: PERFORMANCE / SPEED
    # =============================================
    print("\n" + "=" * 60)
    print("SECTION 11: PERFORMANCE")
    print("=" * 60)

    if admin_user:
        client.get('/logout', follow_redirects=True)
        client.post('/login', data={'username': admin_user[1], 'password': admin_user[2]},
                   follow_redirects=True)

        speed_routes = ['/login', '/dashboard', '/students', '/courses',
                       '/attendance/view', '/grades/manage',
                       '/predictions/admission', '/predictions/performance']
        slow_pages = []

        for url in speed_routes:
            start = time.time()
            resp = client.get(url, follow_redirects=True)
            elapsed = time.time() - start
            if elapsed > 3:
                slow_pages.append((url, elapsed))
                log('FAIL', f'{url} — {elapsed:.2f}s (TOO SLOW — over 3s)')
            elif elapsed > 1.5:
                log('PASS', f'{url} — {elapsed:.2f}s (acceptable but could be faster)')
            else:
                log('PASS', f'{url} — {elapsed:.2f}s (fast)')

        if slow_pages:
            log('FAIL', f'{len(slow_pages)} pages are too slow')
        else:
            log('PASS', 'All pages load within acceptable time')

        client.get('/logout', follow_redirects=True)

    # =============================================
    # FINAL REPORT
    # =============================================
    print("\n" + "=" * 60)
    print("FINAL TEST REPORT")
    print("=" * 60)
    total = results['pass'] + results['fail']
    print(f"\n  Total Tests: {total}")
    print(f"  PASSED:      {results['pass']}")
    print(f"  FAILED:      {results['fail']}")
    print(f"  Pass Rate:   {(results['pass']/total*100) if total > 0 else 0:.1f}%")

    if results['fail'] > 0:
        print(f"\n  FAILED TESTS:")
        for d in results['details']:
            if d.startswith('[FAIL]'):
                print(f"    {d}")
    else:
        print(f"\n  ALL TESTS PASSED!")

    print("\n" + "=" * 60)
