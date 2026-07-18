import streamlit as st
import requests
import json
import random

st.set_page_config(page_title="Fraud Detection Dashboard", layout="centered")

st.title("💳 Credit Card Fraud Detection")
st.markdown("Analyze transactions using an Isolation Forest anomaly detection engine.")

st.divider()

st.subheader("Transaction Details")

# Generate random mock data for testing convenience
if st.button("Generate Random Transaction Features"):
    st.session_state['time'] = random.uniform(0, 170000)
    st.session_state['amount'] = random.uniform(1, 1000)
    for i in range(1, 29):
        st.session_state[f'V{i}'] = random.uniform(-3, 3)

# Layout for inputs
col1, col2 = st.columns(2)
time_val = col1.number_input("Time", value=st.session_state.get('time', 0.0))
amount_val = col2.number_input("Amount ($)", value=st.session_state.get('amount', 50.0))

st.markdown("#### PCA Features (V1 - V28)")
v_features = {}
cols = st.columns(4)
for i in range(1, 29):
    col_idx = (i - 1) % 4
    v_features[f'V{i}'] = cols[col_idx].number_input(f"V{i}", value=st.session_state.get(f'V{i}', 0.0), format="%.4f")

if st.button("Analyze Transaction", type="primary"):
    # Prepare payload
    payload = {"Time": time_val, "Amount": amount_val}
    payload.update(v_features)
    
    # Send request to FastAPI backend
    try:
        response = requests.post("http://127.0.0.1:8000/predict", json=payload)
        response.raise_for_status()
        result = response.json()
        
        st.divider()
        if result['is_fraud']:
            st.error(f"🚨 **{result['status']}**")
            st.warning(f"Anomaly Score: {result['anomaly_score']:.4f}")
        else:
            st.success(f"✅ **{result['status']}**")
            st.info(f"Anomaly Score: {result['anomaly_score']:.4f}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to connect to the backend API. Is FastAPI running? Error: {e}")