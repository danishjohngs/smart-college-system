# Smart College Management System with AI-Based Predictive Analytics

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" />
  <img src="https://img.shields.io/badge/Chart.js-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white" />
  <img src="https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />
</p>

<p align="center">
  <a href="https://smart-college-system.onrender.com">
    <img src="https://img.shields.io/badge/🚀_LIVE_DEMO-Click_Here-success?style=for-the-badge" alt="Live Demo" />
  </a>
</p>

<p align="center">
  A full-stack college management platform powered by machine learning — featuring admission trend prediction, student performance analytics, role-based access control, and an interactive admin dashboard.
</p>

---

## 🌐 Live Demo

**Try it live:** [https://smart-college-system.onrender.com](https://smart-college-system.onrender.com)

> **Note:** The demo is hosted on Render's free tier, which spins down after 15 minutes of inactivity. The first request after a cold start may take ~30 seconds to wake up — subsequent requests are fast.

### Demo Credentials

| Role | Username | Password |
|---|---|---|
| **Admin** | `admin` | `admin123` |
| **Faculty** | `ramesh.kumar` | `faculty123` |
| **Student** | *(any seeded student)* | `student123` |

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [AI/ML Models](#aiml-models)
- [Screenshots](#screenshots)
- [Getting Started](#getting-started-local-development)
- [Project Structure](#project-structure)
- [API Routes](#api-routes)
- [Deployment](#deployment)
- [Roadmap](#roadmap)
- [License](#license)

---

## Overview

Most college management systems handle basic CRUD operations and stop there. This project goes further by embedding **machine learning directly into the administrative workflow** — enabling predictive decision-making for admissions and early intervention for at-risk students.

The system serves three distinct user roles (Admin, Faculty, Student), each with tailored dashboards and permissions, and surfaces AI-driven insights where they matter most: in the admin's daily view.

---

## Key Features

### Core Modules

| Module | Description |
|---|---|
| **Authentication & RBAC** | Role-based login system with session management for Admin, Faculty, and Student roles |
| **Multi-Tenant Architecture** | Each college gets isolated data, users, and ML models via a college code system |
| **Student Management** | Full CRUD operations with detailed student profiles and academic history |
| **Faculty Management** | Admin-controlled faculty records with department associations |
| **Course Management** | Department-wise course catalog with semester and credit tracking |
| **Attendance Tracking** | Mark, view, and generate attendance reports with auto-percentage calculation |
| **Grade Management** | Record grades with auto-calculated CGPA and grade points |
| **Removal Request Workflow** | Multi-step approval system — faculty request, admin approves, records archived |
| **Notification System** | Real-time in-app notifications for approvals, alerts, and system events |
| **Approval System** | Admin approves new faculty/student registrations before granting access |

### AI-Powered Predictive Analytics

| Model | Algorithm | Input Features | Output |
|---|---|---|---|
| **Admission Trend Predictor** | Random Forest Regressor | Year, department, expected applications | Predicted intake + confidence score |
| **Performance Predictor** | Random Forest Classifier | Attendance %, CGPA, internal marks avg | Risk tier: *At Risk · Average · Good · Excellent* |

### Admin Dashboard

- **Real-time statistics** — student count, faculty count, department-wise distribution
- **Interactive Chart.js visualizations** — admission trends, attendance patterns, grade distributions
- **Smart alerts** — automated flags for students classified as "At Risk" by the ML model
- **Quick-action panels** — direct links to management modules from the dashboard

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11, Flask 3.0, Flask-Login |
| **ORM & Database** | SQLAlchemy, SQLite |
| **AI/ML** | Scikit-learn, Pandas, NumPy, Joblib |
| **Frontend** | HTML5, CSS3, JavaScript (ES6), Bootstrap 5 |
| **Data Visualization** | Chart.js |
| **Production Server** | Gunicorn |
| **Deployment** | Render.com (with persistent disk) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Client (Browser)                    │
│              HTML/CSS/JS · Chart.js Dashboards          │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTPS
┌──────────────────────────▼──────────────────────────────┐
│                Gunicorn + Flask Application             │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  Routes  │  │  Auth (RBAC) │  │  Jinja2 Templates │  │
│  │Blueprints│  │  Flask-Login │  │                   │  │
│  └─────┬────┘  └──────────────┘  └───────────────────┘  │
│        │                                                │
│  ┌─────▼─────────────────────────────────────────────┐  │
│  │              Business Logic Layer                 │  │
│  │  ┌─────────────────┐  ┌─────────────────────────┐ │  │
│  │  │ CRUD Operations │  │   ML Prediction Engine  │ │  │
│  │  │ Approval Flows  │  │  · Admission Predictor  │ │  │
│  │  │ Notifications   │  │  · Performance Predictor│ │  │
│  │  └────────┬────────┘  └────────────┬────────────┘ │  │
│  └───────────┼────────────────────────┼──────────────┘  │
│              │                        │                 │
│  ┌───────────▼────────┐  ┌────────────▼─────────────┐   │
│  │  SQLAlchemy ORM    │  │  Scikit-learn (.pkl)     │   │
│  │  SQLite Database   │  │  Per-college Model Files │   │
│  └────────────────────┘  └──────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## AI/ML Models

### Admission Trend Predictor

Predicts future student intake based on 10 years of historical admission data.

- **Algorithm:** Random Forest Regressor
- **Features:** `year`, `department`, `expected_applications`
- **Target:** Predicted students admitted (regression)
- **Output:** Intake prediction with R² confidence score
- **Optimization:** Single-threaded execution (`n_jobs=1`) for sub-200ms response times in serverless environments

### Performance Predictor

Classifies enrolled students into performance tiers for early intervention.

- **Algorithm:** Random Forest Classifier
- **Features:** `attendance_percentage`, `current_cgpa`, `avg_internal_marks`
- **Target:** Multi-class — *At Risk · Average · Good · Excellent*
- **Integration:** Results power the smart alert system on the admin and faculty dashboards

### Model Persistence Pattern

Models are trained once during seeding and serialized to disk via `joblib`. The application loads pre-trained `.pkl` files at runtime, eliminating retraining overhead on every request — a critical optimization for production deployment.

```
ml/saved_models/
├── admission_model_<college_id>.pkl
├── admission_encoder_<college_id>.pkl
└── performance_model_<college_id>.pkl
```

Each college maintains its own isolated model files, supporting the multi-tenant architecture.

---

## Screenshots

> *Screenshots coming soon — add yours in the `docs/screenshots/` folder*
>
> Suggested captures:
> - Login & registration flow
> - Admin dashboard with charts and smart alerts
> - Admission prediction interface
> - Performance prediction with risk tiers
> - Attendance marking & reports
> - Grade management & CGPA tracking
> - Removal request approval workflow

---

## Getting Started (Local Development)

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/danishjohngs/smart-college-system.git
cd smart-college-system

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt

# Seed the database with sample data (creates 100+ students, 20+ faculty, 17 courses, 10 years of admission history)
python seed_data.py

# Start the development server
python app.py
```

The application will be available at **http://localhost:5000**

### Default Credentials (after seeding)

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Faculty | `ramesh.kumar` *(or any seeded faculty)* | `faculty123` |
| Student | *(any seeded student username)* | `student123` |

---

## Project Structure

```
smart-college-system/
│
├── app.py                      # Flask application factory & route registration
├── config.py                   # Environment-based configuration
├── extensions.py               # Flask extension initialization (SQLAlchemy, Login)
├── seed_data.py                # Database seeder with realistic sample data
├── requirements.txt            # Python dependencies
├── render.yaml                 # Render deployment config
├── runtime.txt                 # Python version pin
│
├── ml/                         # Machine Learning module
│   ├── admission_predictor.py  # Admission Random Forest Regressor
│   ├── performance_predictor.py# Performance Random Forest Classifier
│   ├── train_models.py         # Training pipeline & evaluation
│   └── saved_models/           # Serialized model files (per college)
│
├── models/                     # SQLAlchemy ORM models
│   ├── user.py                 # User model with role-based access
│   ├── college.py              # Multi-tenant college isolation
│   ├── student.py              # Student profile & academic records
│   ├── faculty.py              # Faculty records
│   ├── course.py               # Course catalog
│   ├── attendance.py           # Attendance records
│   ├── grade.py                # Grade & CGPA records
│   ├── admission.py            # Historical admission data (ML training)
│   ├── notification.py         # In-app notifications
│   └── removal_request.py      # Student removal workflow
│
├── routes/                     # Flask Blueprint route handlers
│   ├── auth.py                 # Authentication & session management
│   ├── dashboard.py            # Dashboard views per role
│   ├── students.py             # Student management routes
│   ├── faculty.py              # Faculty management routes
│   ├── courses.py              # Course management routes
│   ├── attendance.py           # Attendance routes
│   ├── grades.py               # Grade management routes
│   ├── predictions.py          # ML prediction endpoints
│   ├── api.py                  # JSON API endpoints
│   ├── history.py              # Archive & history routes
│   └── removal_requests.py     # Removal workflow routes
│
├── static/                     # Static assets
│   ├── css/                    # Stylesheets
│   ├── js/                     # Client-side JavaScript & Chart.js configs
│   └── uploads/profiles/       # User profile photos
│
└── templates/                  # Jinja2 HTML templates
    ├── base.html               # Base layout template
    ├── auth/                   # Login, register, approval templates
    ├── dashboard/              # Role-specific dashboards
    ├── students/               # Student management templates
    ├── faculty/                # Faculty management templates
    ├── courses/                # Course management templates
    ├── attendance/             # Attendance templates
    ├── grades/                 # Grade templates
    ├── predictions/            # ML prediction interfaces
    └── removal/                # Removal request templates
```

---

## API Routes

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `GET/POST` | `/login` | User authentication |
| `GET/POST` | `/register` | New user registration |
| `GET` | `/logout` | Session termination |

### Dashboards

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/dashboard` | Role-aware dashboard with charts & alerts |

### Management

| Method | Endpoint | Description |
|---|---|---|
| `GET/POST` | `/students` | Student CRUD |
| `GET/POST` | `/faculty` | Faculty CRUD |
| `GET/POST` | `/courses` | Course management |
| `GET/POST` | `/attendance` | Attendance marking & reports |
| `GET/POST` | `/grades` | Grade management with CGPA calculation |

### Predictions

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/predictions/admission` | Run admission trend prediction |
| `POST` | `/predictions/performance` | Run student performance prediction |

### Workflow

| Method | Endpoint | Description |
|---|---|---|
| `GET/POST` | `/removal-requests` | Create & manage removal requests |
| `GET` | `/history` | Archived records & audit log |

---

## Deployment

### Live on Render

The application is deployed on **Render.com** with the following setup:

- **Runtime:** Python 3.11.9 (pinned via `PYTHON_VERSION` env var)
- **Production server:** Gunicorn
- **Database:** SQLite on a persistent disk mount
- **Auto-deploy:** Triggered on every push to `main` branch
- **Auto-seed:** Database is automatically populated with sample data on first run

### Deploy Your Own Instance

1. Fork this repository
2. Create a [Render](https://render.com) account and connect your GitHub
3. Click **New → Web Service** and select your forked repo
4. Render will auto-detect the `render.yaml` configuration
5. Add the environment variable in the dashboard:
   - `PYTHON_VERSION` → `3.11.9`
   - `SECRET_KEY` → *(auto-generated by Render)*
6. Click **Create Web Service** and wait ~5 minutes for the first build

### Environment Variables

| Variable | Description | Required |
|---|---|---|
| `PYTHON_VERSION` | Python runtime version | Yes (`3.11.9`) |
| `SECRET_KEY` | Flask session encryption key | Yes |
| `DATABASE_URL` | Database connection string (defaults to SQLite) | No |

---

## Roadmap

- [ ] REST API layer with JWT authentication for mobile clients
- [ ] Email/SMS notifications for at-risk student alerts
- [ ] Batch prediction uploads via CSV
- [ ] Model performance monitoring dashboard with drift detection
- [ ] PostgreSQL support for production-scale deployments
- [ ] Docker containerization
- [ ] Automated model retraining on new data
- [ ] Export reports to PDF and Excel

---

## License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Built with Flask, Scikit-learn, and a lot of ☕<br>
  <a href="https://smart-college-system.onrender.com">🚀 View Live Demo</a>
</p>