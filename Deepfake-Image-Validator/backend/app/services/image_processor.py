import cv2
import numpy as np
import base64

class ImageProcessor:
    def __init__(self):
        # Load pre-trained Haar Cascade for Face Detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

    def preprocess_face(self, image_bytes: bytes):
        """Decodes, detects face, crops, and normalizes image for ML input."""
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Invalid image file format.")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Default to entire image if no face isolated
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            face_crop = img[y:y+h, x:x+w]
        else:
            face_crop = img

        # Resize to standard network input dimensions (e.g., 224x224)
        resized = cv2.resize(face_crop, (224, 224))
        
        # Convert BGR to RGB and normalize to [0, 1] range
        rgb_img = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        normalized = rgb_img.astype(np.float32) / 255.0
        
        return img, normalized, faces

    def generate_heatmap(self, original_img, faces, confidence_score: float):
        """Generates a pseudo-heatmap targeting high-frequency artifact vector zones."""
        heatmap = np.zeros_like(original_img, dtype=np.uint8)
        
        if len(faces) > 0 and confidence_score < 0.70:
            (x, y, w, h) = faces[0]
            # Simulate blending artifact detections inside regions of interest (eyes/mouth border bounds)
            cv2.circle(heatmap, (int(x + w/2), int(y + h/2.5)), int(w/4), (0, 0, 255), -1)
            cv2.circle(heatmap, (int(x + w/2), int(y + h/1.6)), int(w/5), (0, 0, 255), -1)
            heatmap = cv2.GaussianBlur(heatmap, (45, 45), 0)
        else:
            # Subtle random noise artifact simulation for highly accurate deepfakes
            cv2.randu(heatmap, (0, 0, 0), (20, 20, 40))
        
        # Blend overlay back with original image
        overlay = cv2.addWeighted(original_img, 0.7, heatmap, 0.3, 0)
        _, buffer = cv2.imencode('.jpg', overlay)
        encoded_img = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded_img}"