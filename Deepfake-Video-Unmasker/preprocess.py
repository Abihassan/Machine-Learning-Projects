import os
import cv2
import urllib.request
from PIL import Image

# 1. Define the local path for the cascade file
cascade_path = "haarcascade_frontalface_default.xml"

# 2. Download the cascade file from OpenCV's official repo if it doesn't exist locally
if not os.path.exists(cascade_path):
    url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
    urllib.request.urlretrieve(url, cascade_path)

# 3. Initialize the Face Detector using the guaranteed local file
face_cascade = cv2.CascadeClassifier(cascade_path)

# 4. Verify it loaded correctly
if face_cascade.empty():
    raise IOError("Failed to load the Haar Cascade XML file. Please check your internet connection.")

def extract_faces(video_path, max_frames=60):
    """
    Extracts chronological face crops from a video evenly using OpenCV.
    """
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Calculate skip rate to evenly sample max_frames across the entire video
    skip_rate = max(1, total_frames // max_frames) if total_frames > 0 else 1
    
    faces = []
    frame_indices = []
    current_frame = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        if current_frame % skip_rate == 0:
            # OpenCV's Haar Cascades require grayscale images for detection
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            detected_faces = face_cascade.detectMultiScale(
                gray_frame, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(60, 60)
            )
            
            if len(detected_faces) > 0:
                # Grab the first face detected
                x, y, w, h = detected_faces[0]
                ih, iw, _ = frame.shape
                
                # Add 20% padding to the bounding box to capture the whole head
                padding = int(h * 0.2)
                y_pad = max(0, y - padding)
                x_pad = max(0, x - padding)
                h_pad = min(ih - y_pad, h + 2 * padding)
                w_pad = min(iw - x_pad, w + 2 * padding)
                
                # Crop from the original color frame, then convert BGR to RGB
                face_crop = frame[y_pad:y_pad+h_pad, x_pad:x_pad+w_pad]
                
                if face_crop.size > 0:
                    face_crop_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
                    faces.append(Image.fromarray(face_crop_rgb))
                    frame_indices.append(current_frame)
                    
        current_frame += 1
        
        # Stop once we have our target number of frames to analyze
        if len(faces) >= max_frames:
            break

    cap.release()
    return faces, frame_indices