import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

# Default path points directly to your downloaded file
DEFAULT_DATA_PATH = os.path.join("data", "train.csv")

def load_and_enrich_ames_data(filepath: str = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """
    Loads the official Ames Housing dataset and enriches it with macroeconomic
    financial features for forecasting.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"❌ Dataset not found at '{filepath}'. Please create a 'data/' folder "
            f"and place 'train.csv' inside it."
        )
    
    df = pd.read_csv(filepath)
    
    # Select the most impactful real estate variables for our web app dashboard
    selected_cols = [
        "GrLivArea",      # Above grade living area square feet
        "BedroomAbvGr",   # Bedrooms above grade
        "FullBath",       # Full bathrooms above grade
        "YearBuilt",      # Original construction date
        "OverallQual",    # Overall material and finish quality (1-10)
        "Neighborhood",   # Physical locations within Ames city limits
        "SalePrice"       # Target variable ($)
    ]
    
    df = df[selected_cols].copy()
    
    # Rename columns to clean, standardized names for our API
    df.rename(columns={
        "GrLivArea": "sqft_living",
        "BedroomAbvGr": "bedrooms",
        "FullBath": "bathrooms",
        "YearBuilt": "year_built",
        "OverallQual": "overall_quality",
        "Neighborhood": "neighborhood",
        "SalePrice": "price"
    }, inplace=True)
    
    # --- ENRICH WITH FINANCIAL FORECASTING METRICS ---
    np.random.seed(42)
    n_samples = len(df)
    
    # Simulate historical mortgage interest rates prevailing at the time of sale (3.0% to 8.5%)
    df["interest_rate"] = np.round(np.random.uniform(3.0, 8.5, size=n_samples), 2)
    
    # Simulate a local School District Quality Score (1.0 to 10.0) correlated with overall quality
    base_school = df["overall_quality"] + np.random.normal(0, 1.0, size=n_samples)
    df["school_score"] = np.round(np.clip(base_school, 1.0, 10.0), 1)
    
    # Adjust price slightly based on the injected interest rate (higher rates depress valuation)
    df["price"] = df["price"] - ((df["interest_rate"] - 5.0) * 3000)
    df["price"] = np.clip(df["price"], 30000, 1500000)
    
    return df

def preprocess_and_split(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    """
    Builds a robust preprocessing pipeline for numerical and categorical Ames features.
    """
    X = df.drop(columns=["price"])
    y = df["price"]
    
    num_cols = ["sqft_living", "bedrooms", "bathrooms", "year_built", "overall_quality", "interest_rate", "school_score"]
    cat_cols = ["neighborhood"]
    
    # Numeric pipeline: Impute missing values with median, then scale
    num_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])
    
    # Categorical pipeline: Impute with 'Missing', then One-Hot Encode
    cat_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="Missing")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer(transformers=[
        ("num", num_pipeline, num_cols),
        ("cat", cat_pipeline, cat_cols)
    ])
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    # Fit on training data ONLY
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)
    
    # Extract column names for downstream feature importance graphs
    encoded_cat_cols = preprocessor.named_transformers_["cat"]["onehot"].get_feature_names_out(cat_cols)
    all_feature_names = num_cols + list(encoded_cat_cols)
    
    X_train_df = pd.DataFrame(X_train_processed, columns=all_feature_names)
    X_test_df = pd.DataFrame(X_test_processed, columns=all_feature_names)
    
    return X_train_df, X_test_df, y_train, y_test, preprocessor

if __name__ == "__main__":
    print("Testing data enrichment pipeline...")
    data = load_and_enrich_ames_data()
    print(f"✅ Successfully loaded and enriched {data.shape[0]} homes from data/train.csv!")
    print(data.head())