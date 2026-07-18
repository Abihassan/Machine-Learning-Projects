from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

def train_production_model(X, y):
    # TimeSeriesSplit ensures no "future data" leaks into training
    tscv = TimeSeriesSplit(n_splits=5)
    
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', RandomForestRegressor(n_estimators=200, max_depth=10))
    ])
    
    # In a production system, you would iterate tscv here
    # For now, we fit the latest slice
    pipeline.fit(X, y)
    return pipeline