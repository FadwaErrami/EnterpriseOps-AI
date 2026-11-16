
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

FEATURES = [
    "level_error",
    "level_critical",
    "message_length",
    "service_encoded",
]

MODEL_PATH = Path(__file__).resolve().parent / "isolation_forest.joblib"


class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(
            n_estimators=150,
            contamination=0.12,
            random_state=42,
        )
        self.is_trained = False

        self.load_model()

    def extract_features(self, logs):
        rows = []

        for log in logs:
            level = log["level"].upper()
            service = log["service"]

            rows.append([
                int(level == "ERROR"),
                int(level == "CRITICAL"),
                len(log["message"]),
                sum(ord(c) for c in service) % 100,
            ])

        return np.array(rows, dtype=float)

    def train(self, logs):
        if len(logs) < 20:
            raise ValueError(
                "At least 20 logs are required to train the model."
            )

        X = self.extract_features(logs)
        self.model.fit(X)
        self.is_trained = True

        joblib.dump(self.model, MODEL_PATH)

        return {
            "trained": True,
            "samples": len(logs),
            "saved": True,
            "model_path": str(MODEL_PATH),
        }

    def load_model(self):
        if MODEL_PATH.exists():
            self.model = joblib.load(MODEL_PATH)
            self.is_trained = True
            print("Isolation Forest model loaded successfully.")
        else:
            print("No saved ML model found. Training is required.")

    def predict(self, logs):
        if not self.is_trained:
            raise RuntimeError(
                "The anomaly detector has not been trained."
            )

        X = self.extract_features(logs)
        predictions = self.model.predict(X)

        results = []

        for log, prediction in zip(logs, predictions):
            results.append({
                **log,
                "ml_anomaly": bool(prediction == -1),
            })

        return results


detector = AnomalyDetector()
