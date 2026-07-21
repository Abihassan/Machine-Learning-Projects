"""
Module B: The Inference Pipeline
Uses pre-trained YOLOv8 to run real-time inference on a camera stream.
"""

import cv2
from ultralytics import YOLO

class QualityControlScanner:
    def __init__(self, model_path="yolov8n.pt", target_class="cell phone", conf_threshold=0.5):
        self.model = YOLO(model_path)
        self.target_class = target_class
        self.conf_threshold = conf_threshold

    def process_frame(self, frame):
        results = self.model(frame, verbose=False)[0]
        
        status = "NO_OBJECT" # Default to nothing detected
        box_color = (128, 128, 128)
        max_confidence = 0.0

        for box in results.boxes:
            class_id = int(box.cls[0])
            class_name = self.model.names[class_id]
            confidence = float(box.conf[0])
            
            if confidence > max_confidence:
                max_confidence = confidence

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            if class_name == self.target_class and confidence >= self.conf_threshold:
                status = "PASS"
                box_color = (0, 255, 0)
                label = f"{class_name.upper()} ({confidence:.2f})"
            else:
                # If it's an object, but not the target object, it's a defect
                if status != "PASS":  # Don't overwrite a PASS if multiple items are in frame
                    status = "FAIL"
                box_color = (0, 0, 255)
                label = f"DEFECT / {class_name.upper()} ({confidence:.2f})"

            cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)

        if status != "NO_OBJECT":
            banner_color = (0, 255, 0) if status == "PASS" else (0, 0, 255)
            cv2.putText(frame, f"STATUS: {status}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, banner_color, 3)

        return frame, status, max_confidence