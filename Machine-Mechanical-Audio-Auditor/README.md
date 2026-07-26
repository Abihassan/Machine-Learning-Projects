# 🏭 Machine Mechanical Audio Auditor

An Edge-AI predictive maintenance tool that diagnoses engine health and detects mechanical anomalies by analyzing the sonic hums of machinery. 

Built with 100% local execution using **YAMNet** (via TensorFlow Hub) for audio feature extraction and **Isolation Forests** for unsupervised anomaly detection.

## 🚀 Features
* **Zero Cloud Dependency:** Runs entirely locally for maximum privacy and edge-deployment capabilities.
* **Pre-trained Audio Embeddings:** Leverages YAMNet to extract 1024-dimensional mathematical representations of sound.
* **Spectral Gating Noise Reduction:** Filters out factory floor background noise before analysis.
* **Interactive Web UI:** Built with Gradio for real-time Mel-spectrogram visualization and anomaly scoring.

## 🛠️ Architecture
1. **Audio Ingestion:** `.wav` file is loaded and resampled to 16kHz mono.
2. **Preprocessing:** Ambient noise is reduced using spectral gating.
3. **Feature Extraction:** Audio passes through YAMNet, outputting an embedding vector.
4. **Anomaly Scoring:** An Isolation Forest compares the embedding against a known "healthy" baseline.
5. **UI:** Gradio displays the diagnosis (Healthy/Anomaly) and the spectrogram.

## 💻 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/Machine-Mechanical-Audio-Auditor.git](https://github.com/YOUR_USERNAME/Machine-Mechanical-Audio-Auditor.git)
   cd Machine-Mechanical-Audio-Auditor