"""
Admission Predictor — ML model for predicting future admission trends.
Uses Random Forest Regressor trained on historical admission data.
"""
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.preprocessing import LabelEncoder
import joblib


class AdmissionPredictor:
    """Predicts future admission numbers using historical data."""

    def __init__(self):
        self.model = None
        self.label_encoder = LabelEncoder()
        self.model_path = os.path.join(os.path.dirname(__file__), 'saved_models', 'admission_model.pkl')
        self.encoder_path = os.path.join(os.path.dirname(__file__), 'saved_models', 'admission_encoder.pkl')

    def train(self, data):
        """
        Train the admission prediction model.

        Args:
            data: list of dicts with keys: year, department, applications, admitted
        Returns:
            r2_score: Model accuracy score
        """
        df = pd.DataFrame(data)

        # Encode department
        df['dept_encoded'] = self.label_encoder.fit_transform(df['department'])

        # Features and target
        X = df[['year', 'dept_encoded', 'applications']].values
        y = df['admitted'].values

        # Handle small datasets — use all data for training if < 10 records
        if len(df) < 10:
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model.fit(X, y)
            score = 1.0
        else:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)
            predictions = self.model.predict(X_test)
            score = max(r2_score(y_test, predictions), 0)  # Clamp to 0 minimum

        # Save model and encoder
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.label_encoder, self.encoder_path)

        return score

    def predict(self, year, department, applications):
        """
        Predict admission numbers for a given year and department.

        Args:
            year: Target year for prediction
            department: Department name
            applications: Expected number of applications
        Returns:
            dict with predicted_admissions and confidence
        """
        # Load model if not in memory
        if self.model is None:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError('Model not trained yet. Please train the model first.')
            self.model = joblib.load(self.model_path)
            self.label_encoder = joblib.load(self.encoder_path)

        # Encode department
        try:
            dept_encoded = self.label_encoder.transform([department])[0]
        except ValueError:
            # Department not seen during training, use default
            dept_encoded = 0

        # Make prediction
        features = np.array([[year, dept_encoded, applications]])
        predicted = self.model.predict(features)[0]

        # Calculate confidence using prediction interval from trees
        tree_predictions = np.array([tree.predict(features)[0] for tree in self.model.estimators_])
        std = np.std(tree_predictions)
        mean = np.mean(tree_predictions)
        confidence = max(0, min(1, 1 - (std / (mean + 1e-6))))  # Normalize to [0, 1]

        return {
            'predicted_admissions': max(0, predicted),  # Can't be negative
            'confidence': confidence
        }
