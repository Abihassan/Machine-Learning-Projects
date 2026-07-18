DEFAULT_TICKER = "NVDA"
DEFAULT_YEARS = 5
AVAILABLE_MODELS = ["Ridge Regression", "Random Forest", "Support Vector Regressor (SVR)"]

LAG_WINDOWS = [1, 2, 3, 5, 10]
SMA_WINDOWS = [10, 20, 50]
EMA_WINDOWS = [12, 26]
RSI_PERIOD = 14
BOLLINGER_WINDOW = 20
BOLLINGER_STD = 2

# Grids
RIDGE_GRID = {"model__alpha": [0.1, 1.0, 10.0]}
RF_GRID = {"model__n_estimators": [100], "model__max_depth": [10]}
SVR_GRID = {"model__C": [1.0, 10.0]}