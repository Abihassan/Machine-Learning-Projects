import cv2
import json
import base64
import logging
import os
import csv
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from ultralytics import YOLO
import uvicorn
from huggingface_hub import hf_hub_download

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup directories for logging
os.makedirs("static/violations", exist_ok=True)
CSV_FILE = "violations.csv"

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Violation", "Image_Path"])

app.mount("/static", StaticFiles(directory="static"), name="static")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Helmet-Inspector")

# 1. Download and Load model explicitly to avoid Windows path errors
try:
    logger.info("Downloading Helmet Detection weights explicitly via huggingface_hub...")
    # This downloads the file safely and returns a valid local Windows path
    model_path = hf_hub_download(repo_id="sharathhhhh/safetyHelmet-detection-yolov8", filename="best.pt")
    
    # Load the model using the local path
    model = YOLO(model_path)
    
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    model = YOLO("yolov8n.pt") # Fallback

# --- DEBUG PRINT ---
print("\n" + "="*50)
print(f"DEBUG - ACTUAL MODEL CLASSES: {model.names}")
print("="*50 + "\n")

# 2. Dynamically map the specific helmet classes
class_names = model.names
helmet_ids = [k for k, v in class_names.items() if "with" in v.lower() and "out" not in v.lower()]
no_helmet_ids = [k for k, v in class_names.items() if "without" in v.lower() or "no" in v.lower()]

# Fallback mapping if metadata is non-standard
if not helmet_ids and not no_helmet_ids:
    helmet_ids, no_helmet_ids = [0], [1]
    
last_logged_time = datetime.min
LOG_COOLDOWN = 3 # Wait 3 seconds between logging the same violation

def log_violation(frame, label):
    """Saves a snapshot and writes to CSV when a missing helmet is detected."""
    global last_logged_time
    now = datetime.now()
    
    if (now - last_logged_time).total_seconds() < LOG_COOLDOWN:
        return None

    last_logged_time = now
    timestamp_str = now.strftime("%Y%m%d_%H%M%S")
    img_filename = f"static/violations/violation_{timestamp_str}.jpg"
    
    cv2.imwrite(img_filename, frame)
    
    with open(CSV_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([now.strftime("%Y-%m-%d %H:%M:%S"), label, img_filename])
        
    return img_filename

def process_frame(frame):
    """Runs direct inference for helmets and draws bounding boxes."""
    results = model.predict(frame, conf=0.25, verbose=False)
    violation_logs = []

    for r in results:
        # --- DEBUG PRINT ---
        if len(r.boxes) > 0:
            print(f"Detected {len(r.boxes)} objects in this frame.")
            
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            
            print(f"Detected Class ID: {cls} with Confidence: {conf:.2f}")
            
            if cls in helmet_ids:
                color = (0, 255, 0)
                label = f"Helmet OK {conf:.2f}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
            elif cls in no_helmet_ids:
                color = (0, 0, 255)
                label = f"Violation {conf:.2f}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                # Trigger logging
                img_path = log_violation(frame, label)
                if img_path:
                    violation_logs.append({"label": label, "snapshot": img_path})

    return frame, violation_logs

@app.websocket("/ws/video")
async def websocket_video_endpoint(websocket: WebSocket):
    await websocket.accept()
    cap = cv2.VideoCapture(0)
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret: break
            
            processed_frame, logs = process_frame(frame)
            _, buffer = cv2.imencode('.jpg', processed_frame)
            b64_img = base64.b64encode(buffer).decode('utf-8')
            
            await websocket.send_text(json.dumps({"frame": b64_img, "logs": logs}))
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    finally:
        cap.release()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)