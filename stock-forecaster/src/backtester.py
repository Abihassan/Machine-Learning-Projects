import numpy as np
import pandas as pd

def simulate_portfolio(actual_close, predicted_close, initial_capital=10000.0):
    df = pd.DataFrame({'Actual': actual_close, 'Predicted': predicted_close})
    df['Signal'] = np.where(df['Predicted'] > df['Actual'].shift(1), 1.0, 0.0)
    df['Strategy_Return'] = df['Signal'].shift(1) * df['Actual'].pct_change()
    df['Equity'] = initial_capital * (1 + df['Strategy_Return'].fillna(0)).cumprod()
    
    return {
        "Final_Value": df['Equity'].iloc[-1],
        "Return_Pct": ((df['Equity'].iloc[-1]/initial_capital)-1)*100,
        "Data": df
    }