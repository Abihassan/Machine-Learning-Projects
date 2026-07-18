import os
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Ames Real Estate Valuation Engine",
    page_icon="📈",
    layout="wide"
)

# Fallback to localhost if the environment variable isn't set
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/predict")
BASELINE_PATH = "models/market_baseline.csv"


# Load neighborhoods dynamically if baseline exists, else use standard Ames list
if os.path.exists(BASELINE_PATH):
    market_df = pd.read_csv(BASELINE_PATH)
    neighborhoods = sorted(market_df["neighborhood"].unique().tolist())
else:
    neighborhoods = ["CollgCr", "Veenker", "Crawfor", "NoRidge", "Mitchel", "Somerst", "NridgHt", "OldTown", "BrkSide", "Sawyer"]

st.title("📈 Real Estate Valuation & Financial Forecasting")
st.markdown("Estimate property valuations in real-time using the **Ames Housing Dataset** and macroeconomic financial indicators.")
st.divider()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🏠 Property & Market Metrics")

neighborhood = st.sidebar.selectbox("Neighborhood", options=neighborhoods, index=0)
sqft = st.sidebar.slider("Living Area (SqFt)", min_value=400, max_value=5000, value=1800, step=50)
overall_quality = st.sidebar.slider("Overall Quality (1-10)", min_value=1, max_value=10, value=7, step=1)
year_built = st.sidebar.slider("Year Built", min_value=1900, max_value=2026, value=2005, step=1)
bedrooms = st.sidebar.selectbox("Bedrooms", options=[1, 2, 3, 4, 5, 6], index=2)
bathrooms = st.sidebar.selectbox("Bathrooms", options=[1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0], index=2)
school_score = st.sidebar.slider("School District Score (1-10)", min_value=1.0, max_value=10.0, value=7.5, step=0.1)
interest_rate = st.sidebar.slider("Mortgage Interest Rate (%)", min_value=3.0, max_value=9.0, value=6.0, step=0.1)

# --- API REQUEST ---
payload = {
    "sqft_living": float(sqft),
    "bedrooms": int(bedrooms),
    "bathrooms": float(bathrooms),
    "year_built": int(year_built),
    "overall_quality": int(overall_quality),
    "neighborhood": str(neighborhood),
    "school_score": float(school_score),
    "interest_rate": float(interest_rate)
}

try:
    response = requests.post(API_URL, json=payload, timeout=5)
    if response.status_code == 200:
        data = response.json()
        val = data["estimated_valuation"]
        lower = data["confidence_interval_95"]["lower_bound"]
        upper = data["confidence_interval_95"]["upper_bound"]
        
        # --- TOP METRICS DISPLAY ---
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Estimated Property Valuation", value=f"${val:,.0f}")
        with col2:
            st.metric(label="95% Confidence Lower Bound", value=f"${lower:,.0f}")
        with col3:
            st.metric(label="95% Confidence Upper Bound", value=f"${upper:,.0f}")
            
        st.divider()
        
        # --- VISUALIZATIONS ---
        chart_col1, chart_col2 = st.columns(2)
        
        # 1. Market Comparison Scatter Plot
        with chart_col1:
            st.subheader("📍 Market Position Analysis")
            if os.path.exists(BASELINE_PATH):
                # Filter background scatter by selected neighborhood if possible
                neigh_df = market_df[market_df["neighborhood"] == neighborhood]
                plot_df = neigh_df if len(neigh_df) > 15 else market_df.sample(n=min(300, len(market_df)), random_state=42)
                
                fig_scatter = px.scatter(
                    plot_df, x="sqft_living", y="price",
                    opacity=0.6, labels={"sqft_living": "Square Feet", "price": "Price ($)"},
                    title=f"Price vs. SqFt (Market: {neighborhood if len(neigh_df) > 15 else 'All Ames'})"
                )
                
                fig_scatter.add_trace(go.Scatter(
                    x=[sqft], y=[val],
                    mode="markers",
                    marker=dict(color="#FF4B4B", size=16, symbol="star", line=dict(color="white", width=2)),
                    name="Your Property"
                ))
                fig_scatter.update_layout(legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.warning("Market baseline data not found. Run train.py first.")
                
        # 2. Valuation Drivers Breakdown
        # Replace the existing chart_col2 logic in dashboard.py with this:
        with chart_col2:
            st.subheader("⚖️ True AI Explainer (SHAP Contributions)")
            st.markdown("*Exact dollar amounts this specific home adds or loses versus the Ames market average.*")
            
            shap_data = data["shap_dollar_impacts"]
            features = list(shap_data.keys())
            impacts = list(shap_data.values())
            colors = ["#00CC96" if x >= 0 else "#EF553B" for x in impacts]
            
            fig_bar = go.Figure(go.Bar(
                x=impacts,
                y=features,
                orientation='h',
                marker_color=colors,
                text=[f"${x:+,.0f}" for x in impacts],
                textposition="auto"
            ))
            fig_bar.update_layout(
                xaxis_title="Dollar Impact on Valuation ($)",
                yaxis=dict(autorange="reversed"),
                margin=dict(l=0, r=0, t=30, b=0)
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
    else:
        st.error(f"Backend API returned an error: {response.text}")

except requests.exceptions.ConnectionError:
    st.error("🚨 Could not connect to the FastAPI backend. Please ensure `uvicorn app.main:app` is running on port 8000.")