import cv2
import math
import time
import os
import urllib.request
import numpy as np

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# 1. Download the pre-trained model automatically if it doesn't exist
MODEL_PATH = 'pose_landmarker_lite.task'
if not os.path.exists(MODEL_PATH):
    print("Downloading MediaPipe Pose Model...")
    url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
    urllib.request.urlretrieve(url, MODEL_PATH)
    print("Download complete.")

def calculate_angle(a, b, c):
    """Calculates the angle between three (x, y) coordinates."""
    radians = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    angle = abs(radians * 180.0 / math.pi)
    if angle > 180.0:
        angle = 360.0 - angle
    return angle

def main():
    # 2. Configure the MediaPipe PoseLandmarker
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    
    # We use VIDEO mode since we are processing a continuous stream of webcam frames
    options = vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )

    # Initialize the video capture (webcam)
    cap = cv2.VideoCapture(0)
    current_pose = 'warrior2'

    # Create the landmarker instance
    with vision.PoseLandmarker.create_from_options(options) as landmarker:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # OpenCV captures in BGR, MediaPipe requires RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to MediaPipe Image object
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # Generate a timestamp (in milliseconds) for the VIDEO mode
            timestamp_ms = int(time.time() * 1000)
            
            # 3. Perform the detection
            detection_result = landmarker.detect_for_video(mp_image, timestamp_ms)

            # 4. Process and draw results
            if detection_result.pose_landmarks:
                # The task API returns a list of poses. We take the first one (index 0)
                pose = detection_result.pose_landmarks[0]
                h, w, _ = frame.shape
                
                # Extract coordinates (MediaPipe returns normalized values 0.0 to 1.0)
                def get_coords(landmark):
                    return [landmark.x * w, landmark.y * h]

                l_shoulder = get_coords(pose[11])
                r_shoulder = get_coords(pose[12])
                l_elbow = get_coords(pose[13])
                r_elbow = get_coords(pose[14])
                l_hip = get_coords(pose[23])
                r_hip = get_coords(pose[24])
                l_knee = get_coords(pose[25])
                r_knee = get_coords(pose[26])
                l_ankle = get_coords(pose[27])
                r_ankle = get_coords(pose[28])

                if current_pose == 'warrior2':
                    left_knee_angle = calculate_angle(l_hip, l_knee, l_ankle)
                    right_knee_angle = calculate_angle(r_hip, r_knee, r_ankle)
                    left_arm_angle = calculate_angle(l_hip, l_shoulder, l_elbow)
                    right_arm_angle = calculate_angle(r_hip, r_shoulder, r_elbow)

                    is_left_front = left_knee_angle < 130
                    front_knee_angle = left_knee_angle if is_left_front else right_knee_angle
                    
                    feedback = "Perfect Warrior II!"
                    color = (0, 255, 0) 
                    
                    if front_knee_angle > 110:
                        feedback = "Bend your front knee more"
                        color = (0, 0, 255)
                    elif front_knee_angle < 75:
                        feedback = "Front knee is bent too much"
                        color = (0, 0, 255)
                    elif left_arm_angle < 75 or left_arm_angle > 105 or right_arm_angle < 75 or right_arm_angle > 105:
                        feedback = "Keep both arms parallel"
                        color = (0, 165, 255)

                    cv2.putText(frame, feedback, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

                # Draw the landmarks manually since Tasks API separates ML from UI rendering
                for landmark in pose:
                    x, y = int(landmark.x * w), int(landmark.y * h)
                    cv2.circle(frame, (x, y), 4, (245, 117, 66), -1)

            cv2.imshow('Modern Tasks API - Yoga Corrector', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()