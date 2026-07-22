import torch
import numpy as np
import streamlit as st
from transformers import AutoImageProcessor, AutoModelForImageClassification
from preprocess import extract_faces

@st.cache_resource
def load_huggingface_model():
    """
    Loads the pre-trained deepfake detector from Hugging Face.
    Cached so it only downloads/loads into memory once per session.
    """
    model_name = "prithivMLmods/deepfake-detector-model-v1"
    processor = AutoImageProcessor.from_pretrained(model_name)
    model = AutoModelForImageClassification.from_pretrained(model_name)
    return processor, model

def analyze_video(video_path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Load Pre-trained Model
    processor, model = load_huggingface_model()
    model.to(device)
    model.eval()
    
    # Extract Faces
    faces, frame_indices = extract_faces(video_path, max_frames=50)
    
    if not faces:
        return [], [], 0, "No faces detected in the video."
    
    scores = []
    
    with torch.no_grad():
        for face in faces:
            # Process image for the pre-trained model
            inputs = processor(images=face, return_tensors="pt").to(device)
            outputs = model(**inputs)
            
            # Apply softmax to get probabilities
            probs = torch.softmax(outputs.logits, dim=-1)
            
            # For this specific model: Class 0 is 'Fake', Class 1 is 'Real'
            fake_prob = probs[0][0].item() 
            scores.append(fake_prob)
            
    # Calculate overall video score by averaging the top 5 most anomalous frames
    # This prevents one bad frame from skewing the result, but catches brief deepfake glitches
    if len(scores) > 5:
        overall_score = np.mean(sorted(scores, reverse=True)[:5])
    else:
        overall_score = np.mean(scores)
        
    verdict = "Fake" if overall_score > 0.6 else "Real"
    
    return scores, frame_indices, overall_score, verdict