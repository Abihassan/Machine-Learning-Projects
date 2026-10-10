🚗 Driver Drowsiness Alert System

A real-time, AI-powered driver monitoring web application that detects signs of drowsiness using facial landmarks and triggers an audio alarm to alert the driver.

Built with FastAPI, OpenCV, and MediaPipe, the system processes webcam frames and presents live monitoring information through a responsive web dashboard.

✨ Features

- Real-Time Drowsiness Monitoring — Processes webcam frames using OpenCV and MediaPipe facial landmark detection.
- Eye Aspect Ratio (EAR) — Displays eye-related measurements to help monitor potential signs of drowsiness.
- Interactive Web Dashboard — Shows monitoring status and provides controls to start or stop the system.
- Audio Alarm Alerts — Uses Pygame to trigger an alarm when drowsiness is detected.
- Asynchronous Alarm Handling — Keeps audio playback separate from the main video-processing workflow to help maintain responsiveness.
- Webcam Resource Management — Releases the webcam when monitoring is stopped, supporting resource efficiency and user privacy.
- Automatic Model Setup — Downloads the required "face_landmarker.task" model if it is missing.
- FastAPI Backend — Connects the frontend dashboard with the computer vision and monitoring logic.

🛠️ Technology Stack

Component| Technologies
Backend| Python, FastAPI, Uvicorn
Computer Vision| OpenCV, MediaPipe Tasks
Frontend| HTML5, CSS3, JavaScript
Templates| Jinja2
Audio Alerts| Pygame
Machine Learning Model| MediaPipe Face Landmarker

🏗️ System Architecture

┌─────────────────────────────┐
│        Webcam Feed          │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│     OpenCV Frame Capture    │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  MediaPipe Face Landmarker  │
│     Facial Landmark Data    │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  Eye Aspect Ratio (EAR)     │
│  Drowsiness Evaluation      │
└──────────────┬──────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
┌──────────────┐ ┌──────────────┐
│ Web Dashboard│ │ Audio Alarm  │
│ Live Status  │ │ Pygame       │
└──────────────┘ └──────────────┘

📂 Project Structure

Drowsiness-Web-App/
│
├── main.py                  # FastAPI application and monitoring logic
├── alarm.wav                # Audio alert sound
├── face_landmarker.task     # MediaPipe model (downloaded if missing)
│
└── templates/
    └── index.html           # Web dashboard interface

⚙️ Prerequisites

Make sure you have the following installed:

- Python 3
- A working webcam
- A supported operating system with webcam access
- An internet connection for the initial model download, if the model is not already present

🚀 Installation and Setup

1. Clone the repository

git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Drowsiness-Web-App

Replace "<YOUR_GITHUB_REPOSITORY_URL>" with your repository's actual Git URL.

2. Create a virtual environment

Windows — PowerShell

python -m venv .venv
.\.venv\Scripts\Activate.ps1

Linux / macOS

python3 -m venv .venv
source .venv/bin/activate

3. Install dependencies

pip install fastapi uvicorn opencv-python mediapipe pygame jinja2

4. Start the application

uvicorn main:app --reload

If the application uses a different startup configuration, follow the FastAPI entry point and settings defined in "main.py".

5. Open the dashboard

Visit the local address in your browser:

http://127.0.0.1:8000

Allow webcam access where required and use the dashboard controls to begin monitoring.

🧠 How It Works

1. Frame Capture: OpenCV captures frames from the webcam.
2. Face Landmark Detection: MediaPipe Face Landmarker identifies facial landmarks.
3. Eye Analysis: The application uses eye-related landmark measurements to calculate the Eye Aspect Ratio (EAR), if implemented in the monitoring logic.
4. Drowsiness Evaluation: The detection logic evaluates eye measurements against its configured conditions.
5. Alert Activation: When the configured drowsiness condition is met, the system triggers the audio alarm.
6. Dashboard Updates: The web interface presents the monitoring status and relevant measurements.

🔊 Audio Alert

The application uses "alarm.wav" as its alert sound and Pygame for audio playback.

Ensure that the audio file is available at the path expected by the application. The alarm should be tested alongside webcam monitoring to confirm that both functions operate correctly.

🔒 Privacy and Safety

- Webcam monitoring is controlled through the application interface.
- The webcam should be released when monitoring is stopped.
- The project is intended as a computer vision prototype and should not be treated as a replacement for vehicle safety systems or responsible driving practices.
- Detection accuracy can vary with lighting, camera placement, facial visibility, and individual differences.

Important: Never rely on this application as the sole means of preventing drowsy driving. If you feel sleepy while driving, stop in a safe location and rest.

🔮 Potential Improvements

- Add configurable EAR thresholds and consecutive-frame detection.
- Track drowsiness duration and display session statistics.
- Introduce head-pose estimation and yawning detection.
- Add event timestamps and monitoring history.
- Improve dashboard visualizations and accessibility.
- Evaluate detection performance under different lighting and camera conditions.

👨‍💻 Author

Abihassan K

- GitHub: "@Abihassan" (https://github.com/Abihassan)
- LinkedIn: "Abihassan K" (https://www.linkedin.com/in/abihassan-k-b8196727a/)
- Portfolio: "Personal Portfolio" (https://abihassan-k-portfolio.vercel.app/)

---

⭐ If you find this project interesting, consider giving the repository a star!
