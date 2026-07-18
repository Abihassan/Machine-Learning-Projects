import cv2
import easyocr
from ultralytics import YOLO

# 1. Load the YOLOv8 model
# Note: For best results, you should download a free pre-trained "license plate" YOLOv8 model 
# from Roboflow Universe or Kaggle instead of the base yolov8n.pt.
model = YOLO('yolov8n.pt') 

# 2. Initialize EasyOCR (Set gpu=True if you have a dedicated graphics card)
reader = easyocr.Reader(['en'], gpu=False) 

# 3. Load your video file
video_path = 'traffic_video.mp4'
cap = cv2.VideoCapture(video_path)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
        
    # Run YOLO detection on the current frame
    results = model(frame)
    
    for r in results:
        boxes = r.boxes
        for box in boxes:
            # Get bounding box coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            # Crop the detected region (the license plate)
            plate_roi = frame[y1:y2, x1:x2]
            
            if plate_roi.size > 0:
                # Preprocess the cropped plate for better OCR accuracy (Grayscale)
                gray_plate = cv2.cvtColor(plate_roi, cv2.COLOR_BGR2GRAY)
                
                # Extract text using EasyOCR
                ocr_results = reader.readtext(gray_plate)
                
                for (bbox, text, prob) in ocr_results:
                    print(f"Detected Plate: {text} | Confidence: {prob:.2f}")
                    
                    # Draw a box and the text on the video frame
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                
    # Display the real-time video processing
    cv2.imshow('Free ALPR System', frame)
    
    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()