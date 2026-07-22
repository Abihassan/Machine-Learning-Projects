import cv2
import json
import base64
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import uvicorn

# Initialize FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PPE-Inspector")

# 1. Load Pre-trained Open-Source YOLOv8 Model directly from Hugging Face Hub
logger.info("Downloading/Loading YOLOv8 weights from Hugging Face...")
try:
    model = YOLO("hf://Hansung-Cho/yolov8-ppe-detection/best.pt")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    raise e

# 2. Dynamically map class IDs from the pre-trained model metadata
class_names = model.names
person_ids = [k for k, v in class_names.items() if "person" in v.lower() or "worker" in v.lower()]
helmet_ids = [k for k, v in class_names.items() if "helmet" in v.lower() or "hardhat" in v.lower() or "hard hat" in v.lower()]
vest_ids = [k for k, v in class_names.items() if "vest" in v.lower()]

logger.info(f"Mapped IDs - Person: {person_ids}, Helmet: {helmet_ids}, Vest: {vest_ids}")

def calculate_iou(box1, box2):
    """Calculates Intersection over Union for spatial overlap mapping."""
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    
    xi1 = max(x1, x2)
    yi1 = max(y1, y2)
    xi2 = min(x1 + w1, x2 + w2)
    yi2 = min(y1 + h1, y2 + h2)
    
    inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
    box1_area = w1 * h1
    box2_area = w2 * h2
    union_area = box1_area + box2_area - inter_area
    
    return inter_area / union_area if union_area > 0 else 0

def process_frame(frame, violation_logs):
    """Runs inference and applies IoU compliance logic."""
    results = model.predict(frame, conf=0.5, verbose=False)
    
    persons, helmets, vests = [], [], []
    
    # Extract bounding boxes and categorize
    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            w, h = x2 - x1, y2 - y1
            cls = int(box.cls[0])
            
            item = {"box": (x1, y1, w, h), "xyxy": (x1, y1, x2, y2)}
            
            if cls in person_ids: persons.append(item)
            elif cls in helmet_ids: helmets.append(item)
            elif cls in vest_ids: vests.append(item)
            
    # Apply logic for each detected person
    for person in persons:
        has_helmet = False
        has_vest = False
        px1, py1, px2, py2 = person["xyxy"]
        
        # Check IoU overlap to associate PPE with the specific person
        for helmet in helmets:
            if calculate_iou(person["box"], helmet["box"]) > 0.1 or (helmet["xyxy"][0] >= px1 and helmet["xyxy"][2] <= px2 and helmet["xyxy"][1] <= py2):
                has_helmet = True
                
        for vest in vests:
            if calculate_iou(person["box"], vest["box"]) > 0.1 or (vest["xyxy"][0] >= px1 and vest["xyxy"][2] <= px2 and vest["xyxy"][1] <= py2):
                has_vest = True
                
        compliant = has_helmet and has_vest
        color = (0, 255, 0) if compliant else (0, 0, 255)
        
        # Draw Output Bounding Boxes
        cv2.rectangle(frame, (px1, py1), (px2, py2), color, 2)
        
        label = "Compliant" if compliant else "Violation:"
        if not has_helmet: label += " No Helmet"
        if not has_vest: label += " No Vest"
        
        cv2.putText(frame, label, (px1, py1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        if not compliant:
            violation_logs.append({"label": label, "box": (px1, py1, px2, py2)})

    return frame, violation_logs

@app.websocket("/ws/video")
async def websocket_video_endpoint(websocket: WebSocket):
    """Handles real-time webcam stream over WebSockets."""
    await websocket.accept()
    cap = cv2.VideoCapture(0) # 0 for default local webcam
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret: break
            
            violation_logs = []
            processed_frame, logs = process_frame(frame, violation_logs)
            
            # Encode frame to Base64 for rapid WebSocket transmission
            _, buffer = cv2.imencode('.jpg', processed_frame)
            b64_img = base64.b64encode(buffer).decode('utf-8')
            
            data = {
                "frame": b64_img,
                "logs": logs
            }
            await websocket.send_text(json.dumps(data))
    except WebSocketDisconnect:
        logger.info("Client disconnected from WebSocket.")
    except Exception as e:
        logger.error(f"WebSocket streaming error: {e}")
    finally:
        cap.release()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)