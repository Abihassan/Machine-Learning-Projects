import cv2
import numpy as np
from ultralytics import YOLO

def process_video(input_path, output_path):
    # 1. Load the YOLOv8 model (the 's' version is a great balance of speed and accuracy)
    # The weights will automatically download for free on the first run.
    print("Loading YOLOv8 model...")
    model = YOLO("yolov8s.pt") 

    # 2. Open the input video
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {input_path}")
        return

    # 3. Get video properties for the output writer
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    # Define the codec and create VideoWriter object (.mp4 format)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    print(f"Processing video: {input_path}")
    frame_count = 0

    # 4. Process the video frame-by-frame
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Run YOLOv8 inference on the frame
        # classes=[0] ensures the model ONLY looks for 'person' (Class 0 in COCO dataset)
        results = model.predict(frame, classes=[0], conf=0.3, verbose=False)
        
        # Extract the number of detected people
        detections = results[0].boxes
        crowd_count = len(detections)

        # Let YOLO draw the bounding boxes on the frame
        annotated_frame = results[0].plot()

        # 5. Create a visually appealing UI overlay for the counter
        # Create a semi-transparent black rectangle for the text background
        overlay = annotated_frame.copy()
        cv2.rectangle(overlay, (20, 20), (350, 100), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, annotated_frame, 0.4, 0, annotated_frame)

        # Add the text overlay
        text = f"Crowd Count: {crowd_count}"
        cv2.putText(annotated_frame, text, (40, 75), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3, cv2.LINE_AA)

        # Write the processed frame to the output video
        out.write(annotated_frame)
        
        frame_count += 1
        if frame_count % 30 == 0:
            print(f"Processed {frame_count} frames...")

    # 6. Clean up resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print(f"Finished processing! Output saved to: {output_path}")

if __name__ == "__main__":
    # Replace 'sample_crowd.mp4' with the path to your overhead video feed
    INPUT_VIDEO = "sample_crowd.mp4" 
    OUTPUT_VIDEO = "output_density.mp4"
    
    process_video(INPUT_VIDEO, OUTPUT_VIDEO)