import cv2
import mediapipe as mp
import math
import time
import pygame
import os
import urllib.request
import numpy as np
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import uvicorn

# --- CONFIGURATION ---
EAR_THRESHOLD = 0.25
CLOSED_TIME_LIMIT = 2.0
ALARM_FILE = "alarm.wav"
MODEL_PATH = "face_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"

# --- GLOBAL STATE ---
STREAM_ACTIVE = False

# --- DOWNLOAD MODEL ---
if not os.path.exists(MODEL_PATH):
    print("Downloading MediaPipe model...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

# --- INITIALIZE AUDIO ---
pygame.mixer.init()
try:
    alarm_sound = pygame.mixer.Sound(ALARM_FILE)
except pygame.error:
    print(f"Error: Could not load '{ALARM_FILE}'.")
    exit()

# --- FASTAPI SETUP ---
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# --- MEDIAPIPE SETUP ---
BaseOptions = mp.tasks.BaseOptions
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=mp.tasks.vision.RunningMode.IMAGE,
    num_faces=1,
    min_face_detection_confidence=0.5
)

RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144] 
LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]

def calculate_ear(landmarks, eye_indices, img_w, img_h):
    coords = [(int(landmarks[i].x * img_w), int(landmarks[i].y * img_h)) for i in eye_indices]
    v1 = math.dist(coords[1], coords[5])
    v2 = math.dist(coords[2], coords[4])
    h = math.dist(coords[0], coords[3])
    return (v1 + v2) / (2.0 * h) if h > 0 else 0, coords

def generate_frames():
    global STREAM_ACTIVE
    STREAM_ACTIVE = True
    
    cap = cv2.VideoCapture(0)
    eyes_closed_start_time = None
    alarm_is_playing = False

    try:
        with mp.tasks.vision.FaceLandmarker.create_from_options(options) as landmarker:
            # The loop now checks the STREAM_ACTIVE flag explicitly
            while cap.isOpened() and STREAM_ACTIVE:
                success, frame = cap.read()
                if not success:
                    break

                frame = cv2.flip(frame, 1)
                img_h, img_w, _ = frame.shape
                
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                results = landmarker.detect(mp_image)

                if results.face_landmarks:
                    landmarks = results.face_landmarks[0]
                    right_ear, right_coords = calculate_ear(landmarks, RIGHT_EYE_INDICES, img_w, img_h)
                    left_ear, left_coords = calculate_ear(landmarks, LEFT_EYE_INDICES, img_w, img_h)
                    avg_ear = (right_ear + left_ear) / 2.0

                    cv2.polylines(frame, [np.array(right_coords)], isClosed=True, color=(0, 255, 0), thickness=1)
                    cv2.polylines(frame, [np.array(left_coords)], isClosed=True, color=(0, 255, 0), thickness=1)

                    if avg_ear < EAR_THRESHOLD:
                        if eyes_closed_start_time is None:
                            eyes_closed_start_time = time.time()
                        else:
                            if time.time() - eyes_closed_start_time >= CLOSED_TIME_LIMIT:
                                cv2.putText(frame, "WARNING: DROWSINESS!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                                if not alarm_is_playing:
                                    alarm_sound.play(-1)
                                    alarm_is_playing = True
                    else:
                        eyes_closed_start_time = None
                        if alarm_is_playing:
                            alarm_sound.stop()
                            alarm_is_playing = False

                    status = "AWAKE" if eyes_closed_start_time is None else "EYES CLOSED"
                    color = (0, 255, 0) if status == "AWAKE" else (0, 165, 255)
                    cv2.putText(frame, f"EAR: {avg_ear:.2f}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.putText(frame, f"Status: {status}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        # Force hardware release when loop breaks
        cap.release()
        pygame.mixer.stop()
        print("Hardware disconnected successfully.")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/stop")
async def stop_system():
    global STREAM_ACTIVE
    # Flip the flag to instantly break the loop in generate_frames()
    STREAM_ACTIVE = False
    pygame.mixer.stop()
    return {"status": "Hardware off"}

if __name__ == "__main__":
    print("Starting server... Open http://127.0.0.1:8000 in your browser.")
    uvicorn.run(app, host="127.0.0.1", port=8000)