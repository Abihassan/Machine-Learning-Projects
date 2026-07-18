# 🚗 Driver Drowsiness Alert System

A real-time, AI-powered web application that monitors a driver's facial landmarks and sounds an alarm if drowsiness is detected. Built with a **FastAPI** backend and an interactive web frontend, this system processes webcam feeds with zero noticeable latency using modern edge-AI computer vision.

## ✨ Features
*   **Real-Time Processing:** Streams webcam frames over HTTP and processes them instantly using MediaPipe's modern Tasks API.
*   **Web-Based Dashboard:** A clean, responsive HTML/CSS/JS interface to monitor status, EAR (Eye Aspect Ratio), and toggle the system on/off.
*   **Hardware Safe-Toggles:** The web interface seamlessly mounts and unmounts the physical webcam hardware to preserve system resources and user privacy.
*   **Asynchronous Audio Alarms:** Uses Pygame to handle non-blocking audio threading, ensuring the video stream never stutters when the alarm triggers.
*   **Auto-Provisioning:** Automatically downloads the required quantized Machine Learning models (`face_landmarker.task`) on the first run.

## 🛠️ Technology Stack
*   **Backend:** Python 3, FastAPI, Uvicorn
*   **Computer Vision:** OpenCV (`cv2`), Google MediaPipe (v11+)
*   **Frontend:** HTML5, CSS3, Vanilla JavaScript, Jinja2 Templates
*   **Audio Processing:** Pygame

## 📂 Project Structure
```text
Drowsiness-Web-App/
│
├── main.py               # Main FastAPI application and streaming logic
├── alarm.wav             # Audio file triggered upon drowsiness detection
├── face_landmarker.task  # MediaPipe ML model (auto-downloads if missing)
│
└── templates/
    └── index.html        # Frontend dashboard interface