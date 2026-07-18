import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

def train_and_save_model():
    print("Loading dataset...")
    # Load the Kaggle dataset
    df = pd.read_csv("creditcard.csv")
    
    # Separate features and labels
    X = df.drop('Class', axis=1)
    y = df['Class']
    
    print("Scaling Amount and Time features...")
    scaler = StandardScaler()
    X[['Time', 'Amount']] = scaler.fit_transform(X[['Time', 'Amount']])
    
    # Initialize Isolation Forest
    # The contamination parameter is set to the approximate ratio of fraud in the dataset (0.17%)
    print("Training Isolation Forest model...")
    model = IsolationForest(
        n_estimators=100, 
        max_samples=len(X), 
        contamination=0.0017, 
        random_state=42, 
        verbose=0
    )
    
    model.fit(X)
    
    # Save the trained model and scaler
    print("Saving the model and scaler...")
    joblib.dump(model, 'isolation_forest_model.pkl')
    joblib.dump(scaler, 'scaler.pkl')
    
    print("Training complete. Pre-trained model saved successfully.")

if __name__ == "__main__":
    train_and_save_model()