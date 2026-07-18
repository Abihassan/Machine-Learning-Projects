from fastapi.testclient import TestClient
from app.main import app

def test_health_check():
    # Using 'with' forces FastAPI to trigger startup/shutdown events
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["model_loaded"] is True

def test_valid_prediction():
    payload = {
        "sqft_living": 2000.0,
        "bedrooms": 3,
        "bathrooms": 2.5,
        "year_built": 2010,
        "overall_quality": 8,
        "neighborhood": "CollgCr",
        "school_score": 8.5,
        "interest_rate": 6.0
    }
    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert "estimated_valuation" in data
        assert data["estimated_valuation"] > 0
        assert "shap_dollar_impacts" in data
        assert "Square Footage" in data["shap_dollar_impacts"]

def test_invalid_input_rejection():
    payload = {
        "sqft_living": -500.0,
        "bedrooms": 3,
        "bathrooms": 2.0,
        "year_built": 2000,
        "overall_quality": 5,
        "neighborhood": "CollgCr",
        "school_score": 5.0,
        "interest_rate": 6.0
    }
    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
        assert response.status_code == 422  # Unprocessable Entity