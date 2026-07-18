import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pyautogui
import numpy as np
import time
import math

# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
CAM_WIDTH, CAM_HEIGHT = 640, 480
FRAME_REDUCTION = 100 
SMOOTHING = 5 
CLICK_THRESHOLD = 30 

prev_x, prev_y = 0, 0
curr_x, curr_y = 0, 0
p_time = 0

# ---------------------------------------------------------
# Initialization - MediaPipe Tasks API
# ---------------------------------------------------------
# Define the options for the Hand Landmarker
base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.7,
    min_tracking_confidence=0.7
)

# Create the Landmarker instance
detector = vision.HandLandmarker.create_from_options(options)

# Initialize Webcam
cap = cv2.VideoCapture(0)
cap.set(3, CAM_WIDTH)
cap.set(4, CAM_HEIGHT)

print("--- INSTRUCTIONS ---")
print("1. Point your Index Finger up to move the mouse.")
print("2. Tap your Thumb to your Index Finger to click.")
print("3. Press 'q' to quit.")

while True:
    success, img = cap.read()
    if not success:
        break

    # Flip image horizontally for natural mirroring
    img = cv2.flip(img, 1)
    
    # Convert the frame to a MediaPipe Image object
    rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    # The VIDEO mode requires a timestamp in milliseconds
    frame_timestamp_ms = int(time.time() * 1000)
    
    # Detect landmarks
    detection_result = detector.detect_for_video(mp_image, frame_timestamp_ms)

    # Draw the active boundary box
    cv2.rectangle(img, (FRAME_REDUCTION, FRAME_REDUCTION), 
                 (CAM_WIDTH - FRAME_REDUCTION, CAM_HEIGHT - FRAME_REDUCTION), 
                 (255, 0, 255), 2)

    # Check if any hands are detected
    if detection_result.hand_landmarks:
        # Get the landmarks for the first detected hand
        hand_landmarks = detection_result.hand_landmarks[0]
        h, w, c = img.shape
        
        # Extract Landmark 8 (Index Finger Tip)
        index_tip = hand_landmarks[8]
        x1, y1 = int(index_tip.x * w), int(index_tip.y * h)
        
        # Extract Landmark 4 (Thumb Tip)
        thumb_tip = hand_landmarks[4]
        x2, y2 = int(thumb_tip.x * w), int(thumb_tip.y * h)

        # 1. Cursor Navigation (Index Finger)
        screen_x = np.interp(x1, (FRAME_REDUCTION, CAM_WIDTH - FRAME_REDUCTION), (0, SCREEN_WIDTH))
        screen_y = np.interp(y1, (FRAME_REDUCTION, CAM_HEIGHT - FRAME_REDUCTION), (0, SCREEN_HEIGHT))

        curr_x = prev_x + (screen_x - prev_x) / SMOOTHING
        curr_y = prev_y + (screen_y - prev_y) / SMOOTHING

        try:
            pyautogui.moveTo(curr_x, curr_y)
        except pyautogui.FailSafeException:
            pass

        prev_x, prev_y = curr_x, curr_y

        # Highlight tracking points
        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (0, 255, 255), cv2.FILLED)

        # 2. Click Mechanism (Distance between Thumb and Index)
        length = math.hypot(x2 - x1, y2 - y1)
        cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)

        if length < CLICK_THRESHOLD:
            cv2.circle(img, (x1, y1), 15, (0, 0, 255), cv2.FILLED)
            cv2.putText(img, "CLICK!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            
            pyautogui.click()
            time.sleep(0.3)

    # Calculate and display FPS
    c_time = time.time()
    if (c_time - p_time) > 0:
        fps = 1 / (c_time - p_time)
        p_time = c_time
        cv2.putText(img, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

    cv2.imshow("MediaPipe Tasks Single Finger Tracker", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()