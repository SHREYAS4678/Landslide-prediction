import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

MODEL_PATH = "model_weights.pkl"

class LandslidePredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        # Dummy training for now
        self._train_dummy_model()

    def _train_dummy_model(self):
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)
        else:
            # Generate synthetic data for basic training
            # Features: soil_moisture, rainfall, temperature, vibration, tilt, humidity
            X = np.random.rand(100, 6)
            # True label formulation (dummy)
            # High moisture, high rain, high tilt -> High Risk
            y = (X[:, 0]*0.3 + X[:, 1]*0.3 + X[:, 4]*0.2 + np.random.rand(100)*0.2)
            y = np.clip(y, 0, 1)
            self.model.fit(X, y)
            joblib.dump(self.model, MODEL_PATH)

    def predict_risk(self, data: list):
        """
        Input data format: [soil_moisture, rainfall, temperature, vibration, tilt, humidity]
        Output: Risk score between 0 and 1
        """
        score = self.model.predict([data])[0]
        # Ensure score is within 0.0 to 1.0
        score = float(np.clip(score, 0.0, 1.0))
        return score

    def determine_risk_level(self, score: float):
        if score <= 0.3:
            return "Safe"
        elif score <= 0.7:
            return "Warning"
        else:
            return "High Risk"

predictor = LandslidePredictor()
