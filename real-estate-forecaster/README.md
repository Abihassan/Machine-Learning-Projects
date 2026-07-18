# 📈 Ames Real Estate Valuation & Explainable AI Engine

A production-grade, full-stack machine learning application that predicts residential property valuations in Ames, Iowa, using an advanced gradient-boosted tree model coupled with macroeconomic financial forecasting indicators. 

Unlike traditional "black-box" models, this engine integrates **SHAP (SHapley Additive exPlanations)** game theory to provide real-time, exact dollar-value transparency for every prediction made.

---

## 🏗️ System Architecture

The application is split into three decoupled, production-ready layers:
1. **Machine Learning Pipeline (`src/`):** Features automated preprocessing, one-hot encoding pipelines via Scikit-Learn, and model selection comparing Random Forest and **XGBoost Regressor** (Final model achieves an $R^2$ score of `0.8858`).
2. **REST API Backend (`app/`):** Built with **FastAPI**, leveraging modern asynchronous `lifespan` architecture, automated documentation, and strict **Pydantic V2** request validation.
3. **Interactive Dashboard (`frontend/`):** A responsive **Streamlit** user interface featuring live **Plotly** market tracking and dynamic feature contribution waterfall charts.

---

## 🛠️ Tech Stack

* **Core ML:** Python 3.11, XGBoost, Scikit-Learn, Pandas, NumPy
* **Explainability:** SHAP (TreeExplainer)
* **Backend API:** FastAPI, Uvicorn, Pydantic V2
* **Testing & MLOps:** Pytest, HTTPX2, GitHub Actions CI/CD
* **Frontend UI:** Streamlit, Plotly, Requests

---

## 🚀 Quick Start (Local Setup)

### 1. Clone & Initialize Environment
```bash
git clone [https://github.com/YOUR_USERNAME/real-estate-forecaster.git](https://github.com/YOUR_USERNAME/real-estate-forecaster.git)
cd real-estate-forecaster

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt