import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import os

class EngineAnomalyDetector:
    def __init__(self, model_path='iso_forest.pkl'):
        self.model_path = model_path
        self.clf = None
        
        if os.path.exists(self.model_path):
            self.clf = joblib.load(self.model_path)
        else:
            # Initialize an empty Isolation Forest if not trained yet
            # contamination defines the expected percentage of anomalies in training data
            self.clf = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
            
    def train_baseline(self, healthy_embeddings):
        """Trains the detector on embeddings of known HEALTHY engines."""
        self.clf.fit(healthy_embeddings)
        joblib.dump(self.clf, self.model_path)
        print("Baseline model trained and saved.")

    def predict(self, embedding):
        """
        Predicts if a new embedding is anomalous.
        Returns: (Status (String), Anomaly Score (Float))
        """
        if self.clf is None:
            return "Untrained", 0.0
            
        embedding_reshaped = embedding.reshape(1, -1)
        
        # Predict returns 1 for inliers (healthy), -1 for outliers (anomaly)
        prediction = self.clf.predict(embedding_reshaped)[0]
        
        # Decision function gives a score: lower (negative) means more anomalous
        score = self.clf.decision_function(embedding_reshaped)[0]
        
        status = "Healthy Engine 🟢" if prediction == 1 else "Anomaly Detected 🔴"
        return status, float(score)