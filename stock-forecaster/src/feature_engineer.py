import numpy as np
import pandas as pd
import yfinance as yf
from config.settings import LAG_WINDOWS, SMA_WINDOWS, EMA_WINDOWS, RSI_PERIOD, BOLLINGER_WINDOW, BOLLINGER_STD

def build_features(df: pd.DataFrame) -> tuple:
    data = df.copy()
    # Basic Tech Indicators
    for lag in LAG_WINDOWS: data[f"Close_Lag_{lag}"] = data["Close"].shift(lag)
    for window in SMA_WINDOWS: data[f"SMA_{window}"] = data["Close"].rolling(window=window).mean()
    data["RSI_14"] = 100 - (100 / (1 + (data["Close"].diff().clip(lower=0).ewm(alpha=1/14).mean() / (-data["Close"].diff().clip(upper=0)).ewm(alpha=1/14).mean())))
    
    # Fourier Cycles
    day_numbers = np.arange(len(data))
    for period in [5, 20]:
        data[f"Fourier_Sin_{period}"] = np.sin(2 * np.pi * day_numbers / period)
        data[f"Fourier_Cos_{period}"] = np.cos(2 * np.pi * day_numbers / period)
        
    # VIX (Simplified)
    data["Macro_VIX"] = 20.0 
    
    data["Target_Next_Close"] = data["Close"].shift(-1)
    data = data.dropna()
    
    features = [c for c in data.columns if c not in ["Open", "High", "Low", "Close", "Volume", "Adj Close", "Target_Next_Close"]]
    return data[features], data["Target_Next_Close"], data["Close"], features