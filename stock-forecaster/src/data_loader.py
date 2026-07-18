from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf


def fetch_live_stock_data(ticker: str, years: int = 5):
    # Ensure it's a string and cleaned up
    ticker = ticker.upper().strip()
    
    # Optional: Logic to handle common errors
    if not ticker:
        raise ValueError("Please enter a valid ticker symbol.")
    
    # ... your existing yfinance code ...
    df = yf.download(ticker, ...)
    
    if df.empty:
        # Instead of just raising a value error, maybe provide a hint
        raise ValueError(f"No market data found for '{ticker}'. Check if this is a valid Yahoo Finance ticker (e.g., 'TSLA' instead of 'tesla').")
    
    return df