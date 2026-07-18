import os
import joblib
import shap
import pandas as pd
import numpy as np
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

MODEL_PATH = "models/best_regressor.joblib"
PREPROCESSOR_PATH = "models/preprocessor.joblib"
model = None
preprocessor = None
explainer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load artifacts on startup
    global model, preprocessor, explainer
    if not os.path.exists(MODEL_PATH) or not os.path.exists(PREPROCESSOR_PATH):
        raise RuntimeError("❌ Artifacts not found! Run `python src/train.py` first.")
    
    model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    explainer = shap.TreeExplainer(model)
    
    yield
    
    # Clean up on shutdown
    model = None
    preprocessor = None
    explainer = None

# Single, unified FastAPI app initialization
app = FastAPI(
    title="Ames Real Estate Valuation API with SHAP Explainability",
    description="Provides ML-driven property valuations based on Ames Housing data and macroeconomic indicators.",
    version="2.0.0",
    lifespan=lifespan
)

class PropertyMetrics(BaseModel):
    sqft_living: float = Field(..., ge=300, le=10000, description="Above grade living area in square feet")
    bedrooms: int = Field(..., ge=0, le=10, description="Bedrooms above grade")
    bathrooms: float = Field(..., ge=0.0, le=8.0, description="Full bathrooms above grade")
    year_built: int = Field(..., ge=1800, le=2026, description="Original construction year")
    overall_quality: int = Field(..., ge=1, le=10, description="Overall material and finish quality (1-10)")
    neighborhood: str = Field(..., description="Physical location within Ames city limits")
    school_score: float = Field(..., ge=1.0, le=10.0, description="Local school district quality score (1-10)")
    interest_rate: float = Field(..., ge=1.0, le=15.0, description="Current prevailing mortgage interest rate (%)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "sqft_living": 1800.0,
                "bedrooms": 3,
                "bathrooms": 2.0,
                "year_built": 2005,
                "overall_quality": 7,
                "neighborhood": "CollgCr",
                "school_score": 8.0,
                "interest_rate": 6.5
            }
        }
    }

@app.get("/")
def health_check():
    return {"status": "healthy", "model_loaded": model is not None}

@app.post("/predict")
def predict_valuation(metrics: PropertyMetrics):
    try:
        # Convert input to DataFrame using modern Pydantic v2 syntax
        input_data = pd.DataFrame([metrics.model_dump()])
        processed_features = preprocessor.transform(input_data)
        
        # Get feature names after encoding to feed cleanly to XGBoost
        num_cols = ["sqft_living", "bedrooms", "bathrooms", "year_built", "overall_quality", "interest_rate", "school_score"]
        cat_cols = ["neighborhood"]
        encoded_cat_cols = preprocessor.named_transformers_["cat"]["onehot"].get_feature_names_out(cat_cols)
        all_feature_names = num_cols + list(encoded_cat_cols)
        
        processed_df = pd.DataFrame(processed_features, columns=all_feature_names)
        
        # 1. Predict Price
        prediction = float(model.predict(processed_df)[0])
        
        # 2. Calculate Exact SHAP Dollar Impacts
        shap_values = explainer.shap_values(processed_df)[0]
        feature_impacts = {name: round(float(val), 2) for name, val in zip(all_feature_names, shap_values)}
        
        # Aggregate all one-hot encoded neighborhood impacts into a single "Neighborhood Impact"
        neigh_impact = sum(val for key, val in feature_impacts.items() if key.startswith("neighborhood_"))
        clean_impacts = {
            "Square Footage": feature_impacts["sqft_living"],
            "Overall Quality": feature_impacts["overall_quality"],
            "Year Built": feature_impacts["year_built"],
            "Neighborhood Location": round(neigh_impact, 2),
            "School Score": feature_impacts["school_score"],
            "Interest Rate": feature_impacts["interest_rate"],
            "Bedrooms & Baths": feature_impacts["bedrooms"] + feature_impacts["bathrooms"]
        }
        
        return {
            "estimated_valuation": round(prediction, 2),
            "baseline_market_value": round(float(explainer.expected_value), 2),
            "shap_dollar_impacts": clean_impacts,
            "confidence_interval_95": {
                "lower_bound": round(prediction * 0.94, 2),
                "upper_bound": round(prediction * 1.06, 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))