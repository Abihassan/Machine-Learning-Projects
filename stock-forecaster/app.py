import streamlit as st
import pandas as pd
from src.data_loader import fetch_live_stock_data
from src.feature_engineer import build_features
from src.model_trainer import train_production_model
from src.risk_engine import calculate_exit_levels
from src.paper_trader import AlpacaPaperTrader

st.set_page_config(page_title="QuantSystem Pro", layout="wide")

# --- SIDEBAR CONTROLS ---
st.sidebar.title("⚡ Quant Control Panel")
st.sidebar.markdown("---")

# ADDED .upper().strip() to handle lowercase and accidental spaces
ticker_input = st.sidebar.text_input("Asset Ticker Symbol", value="NVDA")
ticker = ticker_input.upper().strip() 

# ... rest of your code

with st.sidebar:
    ticker = st.text_input("Asset", "NVDA")
    if st.button("Refresh Analysis"):
        st.cache_data.clear()

# Data Pipeline
@st.cache_data(ttl=300)
def run_pipeline(ticker):
    df = fetch_live_stock_data(ticker)
    X, y, close, _ = build_features(df)
    model = train_production_model(X, y)
    return model, close.iloc[-1]

model, current_price = run_pipeline(ticker)

# Execution Logic
col1, col2 = st.columns(2)
with col1:
    st.subheader("Market Outlook")
    st.metric("Current Price", f"${current_price:.2f}")
    
with col2:
    st.subheader("Risk Management")
    sl, tp = calculate_exit_levels(current_price)
    st.write(f"**Stop Loss:** ${sl:.2f} | **Take Profit:** ${tp:.2f}")
    
    if st.button("🚀 EXECUTE LIVE TRADE"):
        trader = AlpacaPaperTrader()
        # Ensure credentials are in secrets.toml
        order = trader.execute_trade(ticker, True)
        st.success(f"Order Sent: {order}")
        st.balloons()