from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_leaf(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    height, width, _ = img.shape
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 1. Detect Brown Spots (Simulating Early Blight)
    lower_brown = np.array([10, 50, 20])
    upper_brown = np.array([30, 255, 200])
    mask_brown = cv2.inRange(hsv, lower_brown, upper_brown)
    contours_brown, _ = cv2.findContours(mask_brown, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 2. Detect Yellow Spots (Simulating Septoria or Nutrient Deficiency)
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([35, 255, 255])
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    contours_yellow, _ = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    brown_count = 0
    yellow_count = 0

    # Process Brown Contours
    for cnt in contours_brown:
        if cv2.contourArea(cnt) > 150:
            brown_count += 1
            x, y, w, h = cv2.boundingRect(cnt)
            boxes.append({"x": (x / width) * 100, "y": (y / height) * 100, "width": (w / width) * 100, "height": (h / height) * 100})

    # Process Yellow Contours
    for cnt in contours_yellow:
        if cv2.contourArea(cnt) > 150:
            yellow_count += 1
            x, y, w, h = cv2.boundingRect(cnt)
            boxes.append({"x": (x / width) * 100, "y": (y / height) * 100, "width": (w / width) * 100, "height": (h / height) * 100})

    total_spots = brown_count + yellow_count

    # Logic to determine the output based on detected spots
    if total_spots == 0:
        return {
            "disease": "Healthy Leaf",
            "confidence": 98.5,
            "severity": "Low",
            "treatments": [
                "No action needed.",
                "Continue standard watering and sunlight schedule.",
                "Monitor periodically."
            ],
            "boxes": []
        }

    # Calculate dynamic severity
    severity = "Low"
    if total_spots > 3: severity = "Medium"
    if total_spots > 8: severity = "High"

    # Calculate a simulated confidence score based on spot clarity
    confidence = round(80.0 + (min(total_spots, 15) * 1.1), 1)

    # Determine primary disease
    if brown_count >= yellow_count:
        return {
            "disease": "Early Blight",
            "confidence": confidence,
            "severity": severity,
            "treatments": [
                "Remove and destroy infected lower leaves.",
                "Apply copper-based organic fungicide.",
                "Ensure proper spacing between plants for airflow."
            ],
            "boxes": boxes
        }
    else:
        return {
            "disease": "Septoria Leaf Spot",
            "confidence": confidence,
            "severity": severity,
            "treatments": [
                "Avoid overhead watering to keep foliage dry.",
                "Apply neem oil or sulfur-based fungicides.",
                "Clear fallen debris around the plant base."
            ],
            "boxes": boxes
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)