"""
Module A: Data Capture
Captures images from the webcam and categorizes them into train/val folders
for YOLOv8 classification training.
"""

import cv2
import os
import random
import time

# --- Configuration ---
CAMERA_ID = 0  # Change to 1, 2, etc. if using an external USB camera
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "images"))
CLASSES = ["pass", "fail"]
SPLIT_RATIO = 0.8  # 80% Train, 20% Val

def create_directories():
    """Ensure the directory structure exists."""
    for split in ["train", "val"]:
        for cls in CLASSES:
            os.makedirs(os.path.join(BASE_DIR, split, cls), exist_ok=True)
    print(f"[INFO] Directory structure verified at {BASE_DIR}")

def capture_data():
    """Main loop to capture webcam frames and save them based on user input."""
    cap = cv2.VideoCapture(CAMERA_ID)
    
    if not cap.isOpened():
        print(f"[ERROR] Could not open camera {CAMERA_ID}. Please check connections.")
        return

    print("[INFO] Camera started.")
    print("Press 'p' to save as PASS (Good component).")
    print("Press 'f' to save as FAIL (Defective component).")
    print("Press 'q' to QUIT.")

    count_pass = 0
    count_fail = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame. Exiting...")
            break

        # Display instructions and counts on the frame
        display_frame = frame.copy()
        cv2.putText(display_frame, f"PASS: {count_pass} | FAIL: {count_fail}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(display_frame, "Keys: 'p'=Pass, 'f'=Fail, 'q'=Quit", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        cv2.imshow("Data Capture - Quality Control", display_frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("[INFO] Exiting data capture...")
            break
            
        elif key in [ord('p'), ord('f')]:
            # Determine class
            label = "pass" if key == ord('p') else "fail"
            
            # Determine train/val split
            split = "train" if random.random() < SPLIT_RATIO else "val"
            
            # Generate unique filename based on timestamp
            filename = f"{label}_{int(time.time() * 1000)}.jpg"
            save_path = os.path.join(BASE_DIR, split, label, filename)
            
            # Save the original frame (without the text overlay)
            cv2.imwrite(save_path, frame)
            print(f"[SAVED] {filename} -> {split}/{label}")
            
            if label == "pass":
                count_pass += 1
            else:
                count_fail += 1

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    create_directories()
    capture_data()