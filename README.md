# Smart College Management System with AI-Based Predictive Analytics

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" />
  <img src="https://img.shields.io/badge/Chart.js-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" />
</p>

<p align="center">
  A full-stack college management platform powered by machine learning — featuring admission prediction, student performance analytics, role-based access control, and an interactive admin dashboard.
</p>

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [AI/ML Models](#aiml-models)
- [Screenshots](#screenshots)
- [Getting Started](#getting-started)
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
| **Student Management** | Full CRUD operations with detailed student profiles and academic history |
| **Faculty Management** | Admin-controlled faculty records with department associations |
| **Course Management** | Department-wise course catalog with enrollment tracking |
| **Attendance Tracking** | Mark, view, and generate attendance reports per course and student |
| **Grade Management** | Record grades, auto-calculate CGPA, and track academic progression |
| **Unified Reports** | Consolidated reporting page with exportable attendance, grade, and performance data |

### AI-Powered Predictive Analytics

| Model | Input Features | Output |
|---|---|---|
| **Admission Predictor** | Entrance exam score, 12th-grade marks, department preference | Admission likelihood (Accept / Reject) with confidence score |
| **Performance Predictor** | Attendance rate, current grades, historical performance | Risk category: *At Risk · Average · Good · Excellent* |

### Admin Dashboard

- **Real-time statistics** — student count, faculty count, department-wise enrollment
- **Interactive Chart.js visualizations** — department distribution, attendance trends, admission rates, grade analytics
- **Smart alerts** — automated flags for students classified as "At Risk" by the ML model
- **Quick-action panels** — direct links to management modules from the dashboard

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.10+, Flask, Flask-Login |
| **ORM & Database** | SQLAlchemy, SQLite |
| **AI/ML** | Scikit-learn, Pandas, NumPy |
| **Frontend** | HTML5, CSS3, JavaScript (ES6) |
| **Data Visualization** | Chart.js |
| **Deployment** | Vercel (serverless) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Client (Browser)                    │
│              HTML/CSS/JS · Chart.js Dashboards          │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP
┌──────────────────────────▼──────────────────────────────┐
│                    Flask Application                    │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  Routes   │  │  Auth (RBAC) │  │  Jinja2 Templates │  │
│  │ Blueprints│  │  Flask-Login │  │                   │  │
│  └─────┬────┘  └──────────────┘  └───────────────────┘  │
│        │                                                │
│  ┌─────▼─────────────────────────────────────────────┐  │
│  │              Business Logic Layer                 │  │
│  │  ┌─────────────────┐  ┌─────────────────────────┐ │  │
│  │  │ CRUD Operations │  │   ML Prediction Engine   │ │  │
│  │  │                 │  │  · Admission Predictor   │ │  │
│  │  │                 │  │  · Performance Predictor  │ │  │
│  │  └────────┬────────┘  └────────────┬────────────┘ │  │
│  └───────────┼────────────────────────┼──────────────┘  │
│              │                        │                 │
│  ┌───────────▼────────┐  ┌────────────▼─────────────┐  │
│  │  SQLAlchemy ORM    │  │  Scikit-learn (.pkl)     │  │
│  │  SQLite Database   │  │  Trained Model Files     │  │
│  └────────────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## AI/ML Models

### Admission Predictor

Predicts whether a prospective student should be admitted based on academic credentials.

- **Algorithm:** Logistic Regression / Random Forest (best selected via cross-validation)
- **Features:** `entrance_score`, `twelfth_percentage`, `department_id`
- **Target:** Binary classification (Admit / Reject)
- **Training:** Synthetic dataset generated from realistic admission criteria
- **Persistence:** Serialized via `joblib` to `ml/saved_models/`

### Performance Predictor

Classifies enrolled students into performance tiers for early intervention.

- **Algorithm:** Decision Tree / Random Forest Classifier
- **Features:** `attendance_percentage`, `current_cgpa`, `assignment_scores`
- **Target:** Multi-class (At Risk / Average / Good / Excellent)
- **Integration:** Results feed directly into the admin dashboard's smart alert system

### Training Pipeline

```bash
# Retrain models with updated data
python ml/train_models.py
```

Models are versioned in `ml/saved_models/` and loaded at application startup.

---

## Screenshots

> *Add screenshots of your application here*
>
> Suggested screenshots:
> - Login page
> - Admin dashboard with charts and smart alerts
> - Admission prediction form and results
> - Performance prediction output
> - Student/Faculty management views
> - Attendance and grade reports

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
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

# Seed the database with sample data
python seed_data.py

# Start the development server
python app.py
```

The application will be available at **http://localhost:5000**

### Demo Credentials

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Faculty | `faculty1` | `faculty123` |
| Student | `student1` | `student123` |

---

## Project Structure

```
smart-college-system/
│
├── app.py                      # Application entry point & route registration
├── config.py                   # Environment-based configuration
├── extensions.py               # Flask extension initialization (SQLAlchemy, Login)
├── seed_data.py                # Database seeder with realistic sample data
├── requirements.txt            # Python dependencies
├── vercel.json                 # Vercel serverless deployment config
│
├── ml/                         # Machine Learning module
│   ├── admission_predictor.py  # Admission prediction logic & API
│   ├── performance_predictor.py# Performance classification logic & API
│   ├── train_models.py         # Model training & evaluation pipeline
│   └── saved_models/           # Serialized model files (.pkl)
│
├── models/                     # SQLAlchemy ORM models
│   ├── user.py                 # User model with role-based access
│   ├── student.py              # Student profile & academic records
│   ├── faculty.py              # Faculty records
│   ├── course.py               # Course catalog
│   ├── attendance.py           # Attendance records
│   └── grade.py                # Grade & CGPA records
│
├── routes/                     # Flask Blueprint route handlers
│   ├── auth.py                 # Authentication & session management
│   ├── admin.py                # Admin dashboard & management routes
│   ├── student.py              # Student-facing routes
│   ├── faculty.py              # Faculty-facing routes
│   ├── prediction.py           # ML prediction API endpoints
│   └── reports.py              # Unified reporting routes
│
├── static/                     # Static assets
│   ├── css/                    # Stylesheets
│   ├── js/                     # Client-side JavaScript & Chart.js configs
│   └── images/                 # UI assets
│
└── templates/                  # Jinja2 HTML templates
    ├── base.html               # Base layout template
    ├── dashboard/              # Dashboard views per role
    ├── auth/                   # Login & registration templates
    ├── students/               # Student management templates
    ├── faculty/                # Faculty management templates
    ├── courses/                # Course management templates
    ├── predictions/            # ML prediction form & result templates
    └── reports/                # Report generation templates
```

---

## API Routes

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `GET/POST` | `/login` | User authentication |
| `GET` | `/logout` | Session termination |

### Admin Operations

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/admin/dashboard` | Dashboard with charts & alerts |
| `GET/POST` | `/admin/students` | Student CRUD |
| `GET/POST` | `/admin/faculty` | Faculty CRUD |
| `GET/POST` | `/admin/courses` | Course management |

### Predictions

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/predict/admission` | Run admission prediction |
| `POST` | `/predict/performance` | Run performance prediction |

### Reports

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/reports` | Unified reports dashboard |
| `GET` | `/reports/attendance` | Attendance reports |
| `GET` | `/reports/grades` | Grade reports |

---

## Deployment

### Vercel (Serverless)

The project includes a `vercel.json` configuration for serverless deployment.

1. Install the [Vercel CLI](https://vercel.com/docs/cli)
2. Set the required environment variable:
   ```bash
   vercel env add SECRET_KEY
   ```
3. Deploy:
   ```bash
   vercel --prod
   ```

### Environment Variables

| Variable | Description | Required |
|---|---|---|
| `SECRET_KEY` | Flask session encryption key | Yes |
| `DATABASE_URL` | Database connection string (defaults to SQLite) | No |

---

## Roadmap

- [ ] REST API layer with JWT authentication
- [ ] Email/SMS notifications for at-risk student alerts
- [ ] Batch prediction uploads via CSV
- [ ] Model performance monitoring dashboard
- [ ] Docker containerization
- [ ] PostgreSQL support for production

---

## License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Built with Flask, Scikit-learn, and a lot of ☕
</p>