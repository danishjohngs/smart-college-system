# Smart College Management System with AI-Based Predictive Analytics

A full-stack college management web application with AI/ML-powered predictive analytics for student admissions and academic performance.

**BCA Final Year Project — St Benedict Academy, 2026**

## Authors
- Adhithyan
- Jaymon
- Joel
- Joy

## Tech Stack
- **Backend:** Python Flask
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite (SQLAlchemy ORM)
- **AI/ML:** Scikit-learn, Pandas, NumPy
- **Charts:** Chart.js

## Features

### Core Modules
- **Authentication** — Role-based login (Admin / Faculty / Student)
- **Student Management** — Full CRUD with profiles
- **Faculty Management** — Admin-controlled CRUD
- **Course Management** — Department-wise course handling
- **Attendance Tracking** — Mark, view, and generate reports
- **Grade Management** — Manage grades, auto-calculate CGPA

### AI-Powered Predictions
- **Admission Prediction** — ML model predicts admission likelihood based on entrance scores, 12th marks, and department
- **Performance Prediction** — Predicts student academic performance category (At Risk / Average / Good / Excellent)

### Admin Dashboard
- Interactive Chart.js visualizations (department stats, attendance, admissions, grades)
- Smart alerts for at-risk students identified by the AI model
- Real-time statistics overview

## Setup (Local Development)

```bash
# Clone the repo
git clone https://github.com/<your-username>/smart-college-system.git
cd smart-college-system

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt

# Seed the database with sample data
python seed_data.py

# Run the app
python app.py
```

Visit `http://localhost:5000`

### Default Login Credentials (after seeding)
| Role    | Username | Password   |
|---------|----------|------------|
| Admin   | admin    | admin123   |
| Faculty | faculty1 | faculty123 |
| Student | student1 | student123 |

## Deployment (Vercel)
This project is configured for Vercel deployment via `vercel.json`. Set the following environment variable in your Vercel project settings:

- `SECRET_KEY` — A strong random string for Flask session security

## Project Structure
```
smart-college-system/
├── app.py                  # Flask application entry point
├── config.py               # Configuration settings
├── extensions.py           # Flask extensions (SQLAlchemy, Login)
├── seed_data.py            # Database seeder with sample data
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel deployment config
├── ml/                     # Machine Learning models
│   ├── admission_predictor.py
│   ├── performance_predictor.py
│   ├── train_models.py
│   └── saved_models/       # Trained model files (.pkl)
├── models/                 # SQLAlchemy database models
├── routes/                 # Flask route blueprints
├── static/                 # CSS, JS, images
└── templates/              # Jinja2 HTML templates
```

## License
Academic project — St Benedict Academy, 2026.
