"""
Module A: YOLOv8 Training Script
Trains a YOLOv8 classification model on the captured dataset.
"""

import os
from ultralytics import YOLO

def train_model():
    # Define absolute path to dataset to avoid Ultralytics pathing issues
    dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "images"))
    
    if not os.path.exists(dataset_path):
        print(f"[ERROR] Dataset path {dataset_path} does not exist. Run data_capture.py first.")
        return

    print(f"[INFO] Initializing YOLOv8 classification training on dataset: {dataset_path}")

    # Load a pre-trained YOLOv8 Nano classification model
    # Nano (n) is ideal for real-time, high-speed inference on factory lines
    model = YOLO("yolov8n-cls.pt")

    # Train the model
    # epochs=20 is a starting point. Increase if underfitting.
    # imgsz=224 is standard for YOLOv8 classification.
    results = model.train(
        data=dataset_path,
        epochs=20,
        imgsz=224,
        batch=16,
        project="models",      # Save results in the models/ directory
        name="qc_classifier"   # Subfolder name for this training run
    )

    print("[INFO] Training complete!")
    print("[INFO] Your best weights are saved at: models/qc_classifier/weights/best.pt")

if __name__ == "__main__":
    train_model()