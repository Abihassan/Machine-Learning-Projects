from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os

app = FastAPI(title="Fake News Detector API")

# Allow requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Model and Vectorizer safely
try:
    vectorizer = joblib.load('vectorizer.pkl')
    model = joblib.load('model.pkl')
except Exception as e:
    print("Error loading model. Make sure you run train_model.py first!")

class TextRequest(BaseModel):
    text: str

@app.post("/api/predict")
async def predict_news(request: TextRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    # Vectorize the incoming text
    vectorized_text = vectorizer.transform([request.text])
    
    # Make prediction and get probabilities
    prediction = model.predict(vectorized_text)[0]
    probabilities = model.predict_proba(vectorized_text)[0]
    
    # Extract confidence score (probability of the chosen class)
    confidence = max(probabilities) * 100
    
    return {
        "prediction": prediction,
        "confidence": round(confidence, 2)
    }