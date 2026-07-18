# Online Comment Toxicity Filter 🛡️

A full-stack web application that automatically analyzes and moderates user comments using Machine Learning. Built with **FastAPI**, **SQLite**, and **Hugging Face Transformers**.

## 🚀 Features

*   **Real-time ML Inference:** Uses the `unitary/toxic-bert` model to instantly evaluate the toxicity of incoming comments.
*   **Auto-Moderation:** Automatically flags comments that exceed a customizable toxicity threshold (e.g., > 65%).
*   **Admin Dashboard:** A clean, built-in frontend dashboard powered by Tailwind CSS to monitor the moderation queue and review comment scores.
*   **Zero-Setup Database:** Uses a local SQLite database to persist comments right out-of-the-box.
*   **100% Free & Local:** No paid APIs (like Perspective API) required. The ML model runs locally on your machine.

## 🛠️ Tech Stack

*   **Backend:** Python, FastAPI
*   **Machine Learning:** Hugging Face `transformers`, PyTorch
*   **Database:** SQLite (via SQLAlchemy)
*   **Frontend:** Vanilla HTML, JavaScript, Tailwind CSS (via CDN)

## 📋 Prerequisites

*   Python 3.8 or higher installed on your system.

## ⚙️ Installation & Setup

1. **Setup your project folder:**
   Ensure `main.py`, `index.html`, and `requirements.txt` are in the same directory.

2. **Install Dependencies:**
   Open your terminal in the project folder and run:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: The first time you start the server, it will download the `toxic-bert` ML model from Hugging Face, which is roughly 400MB. This only happens once.)*

3. **Run the Application:**
   Start the FastAPI development server using Uvicorn:
   ```bash
   uvicorn main:app --reload
   ```

4. **Access the Dashboard:**
   Open your web browser and navigate to:
   **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

## 🎛️ Customization

**Adjusting the Toxicity Threshold:**
By default, comments with a toxicity score strictly above **65%** (0.65) are flagged. 
If you want to make the filter stricter (for example, to catch borderline inappropriate comments), edit `main.py`:

Find this line in the `submit_comment` function:
```python
is_flagged = score > 0.65
```
Change it to a lower value, such as `0.50` (50%), and restart the server.
