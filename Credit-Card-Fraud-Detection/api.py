from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd

# Initialize FastAPI app
app = FastAPI(title="Fraud Detection API")

# Load pre-trained models on startup
try:
    model = joblib.load('isolation_forest_model.pkl')
    scaler = joblib.load('scaler.pkl')
except FileNotFoundError:
    raise RuntimeError("Model files not found. Please run train.py first.")

# Define the expected data structure for a transaction
class TransactionData(BaseModel):
    Time: float
    V1: float; V2: float; V3: float; V4: float; V5: float
    V6: float; V7: float; V8: float; V9: float; V10: float
    V11: float; V12: float; V13: float; V14: float; V15: float
    V16: float; V17: float; V18: float; V19: float; V20: float
    V21: float; V22: float; V23: float; V24: float; V25: float
    V26: float; V27: float; V28: float
    Amount: float

@app.post("/predict")
def predict_fraud(transaction: TransactionData):
    try:
        # Convert incoming JSON payload to DataFrame
        data_dict = transaction.model_dump()
        df = pd.DataFrame([data_dict])
        
        # Scale Time and Amount
        df[['Time', 'Amount']] = scaler.transform(df[['Time', 'Amount']])
        
        # Predict anomaly (-1 for outliers/fraud, 1 for inliers/normal)
        prediction = model.predict(df)
        anomaly_score = model.decision_function(df)
        
        is_fraud = bool(prediction[0] == -1)
        
        return {
            "is_fraud": is_fraud,
            "anomaly_score": float(anomaly_score[0]),
            "status": "Fraudulent Transaction Detected" if is_fraud else "Transaction Approved"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Run the server using: uvicorn api:app --reload