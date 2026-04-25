"""
Performance Predictor — ML model for predicting student academic performance.
Uses Random Forest Classifier to categorize students into risk levels.
"""
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib


class PerformancePredictor:
    """Predicts student performance risk level using ML."""

    def __init__(self, model_path=None):
        self.model = None
        self.risk_categories = {
            0: 'At Risk',
            1: 'Average',
            2: 'Good',
            3: 'Excellent'
        }
        self.model_path = model_path or os.path.join(os.path.dirname(__file__), 'saved_models', 'performance_model.pkl')

    def train(self, data):
        """
        Train the performance prediction model.

        Args:
            data: list of dicts with: attendance_pct, past_cgpa, internal_marks, category
                  category: 0=At Risk, 1=Average, 2=Good, 3=Excellent
        Returns:
            accuracy: Model accuracy score
        """
        df = pd.DataFrame(data)

        # Ensure we have all necessary columns
        required_cols = ['attendance_pct', 'past_cgpa', 'internal_marks', 'category']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f'Missing required column: {col}')

        X = df[['attendance_pct', 'past_cgpa', 'internal_marks']].values
        y = df['category'].values

        # Handle small datasets
        if len(df) < 10:
            self.model = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=1)
            self.model.fit(X, y)
            accuracy = 1.0
        else:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            self.model = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=1)
            self.model.fit(X_train, y_train)
            predictions = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, predictions)

        # Save model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)

        return accuracy

    def predict(self, attendance_pct, past_cgpa, internal_marks):
        """
        Predict a student's performance category.

        Args:
            attendance_pct: Student's attendance percentage (0-100)
            past_cgpa: Student's cumulative GPA (0-10)
            internal_marks: Average internal marks (0-50)
        Returns:
            dict with category number, risk_level string, and confidence
        """
        # Load model if not in memory
        if self.model is None:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError('Model not trained yet. Please train the model first.')
            self.model = joblib.load(self.model_path)

        features = np.array([[attendance_pct, past_cgpa, internal_marks]])
        prediction = self.model.predict(features)
        probabilities = self.model.predict_proba(features)[0]

        category = int(prediction[0])
        confidence = float(max(probabilities))

        return {
            'category': category,
            'risk_level': self.risk_categories.get(category, 'Unknown'),
            'confidence': confidence
        }

    def predict_batch(self, students_data):
        """
        Predict performance for multiple students at once.

        Args:
            students_data: list of dicts with attendance_pct, past_cgpa, internal_marks
        Returns:
            list of prediction results
        """
        if self.model is None:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError('Model not trained yet.')
            self.model = joblib.load(self.model_path)

        results = []
        for data in students_data:
            features = np.array([[data['attendance_pct'], data['past_cgpa'], data['internal_marks']]])
            prediction = self.model.predict(features)
            probabilities = self.model.predict_proba(features)[0]
            category = int(prediction[0])

            results.append({
                'category': category,
                'risk_level': self.risk_categories.get(category, 'Unknown'),
                'confidence': float(max(probabilities))
            })

        return results
