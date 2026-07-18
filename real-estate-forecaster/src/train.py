import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor
from data_pipeline import load_and_enrich_ames_data, preprocess_and_split

def evaluate_model(name: str, model, X_test, y_test):
    predictions = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    
    print(f"--- {name} Performance ---")
    print(f"RMSE: ${rmse:,.2f}")
    print(f"MAE:  ${mae:,.2f}")
    print(f"R²:   {r2:.4f}\n")
    return rmse, r2

def train_pipeline():
    print("1. Loading Ames Housing data from data/train.csv...")
    df = load_and_enrich_ames_data()
    X_train, X_test, y_train, y_test, preprocessor = preprocess_and_split(df)
    
    print("2. Training Random Forest Regressor...")
    rf_model = RandomForestRegressor(n_estimators=150, max_depth=15, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_rmse, _ = evaluate_model("Random Forest", rf_model, X_test, y_test)
    
    print("3. Training XGBoost Regressor...")
    xgb_model = XGBRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
    xgb_model.fit(X_train, y_train)
    xgb_rmse, _ = evaluate_model("XGBoost", xgb_model, X_test, y_test)
    
    best_model = xgb_model if xgb_rmse < rf_rmse else rf_model
    best_model_name = "XGBoost" if xgb_rmse < rf_rmse else "Random Forest"
    print(f"🏆 Winner: {best_model_name}! Saving artifacts to /models...")
    
    os.makedirs("models", exist_ok=True)
    
    # Save model and the full preprocessor pipeline
    joblib.dump(best_model, "models/best_regressor.joblib")
    joblib.dump(preprocessor, "models/preprocessor.joblib")
    
    # Save baseline market dataset for frontend scatter plots
    df.to_csv("models/market_baseline.csv", index=False)
    print("✅ Real estate model, preprocessor, and baseline market data successfully saved!")

if __name__ == "__main__":
    train_pipeline()