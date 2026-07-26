import os
import numpy as np
import glob
from audio_processor import load_audio
from model_inference import extract_embeddings
from anomaly_detector import EngineAnomalyDetector

def train_real_baseline(data_directory):
    print(f"Scanning directory '{data_directory}' for healthy audio samples...")
    audio_files = glob.glob(os.path.join(data_directory, '*.wav'))
    
    if not audio_files:
        print("❌ No .wav files found! Please add some healthy engine sounds to the folder.")
        return

    healthy_embeddings = []
    
    for file_path in audio_files:
        print(f"Processing: {os.path.basename(file_path)}")
        try:
            # 1. Load and clean the audio
            wav = load_audio(file_path)
            
            # 2. Extract the mathematical embedding using YAMNet
            embedding = extract_embeddings(wav)
            healthy_embeddings.append(embedding)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
    # Convert list to numpy array
    embedding_matrix = np.vstack(healthy_embeddings)
    print(f"✅ Extracted features for {len(healthy_embeddings)} files. Matrix shape: {embedding_matrix.shape}")
    
    # 3. Train the Anomaly Detector
    print("Training Isolation Forest baseline...")
    detector = EngineAnomalyDetector()
    detector.train_baseline(embedding_matrix)
    print("🎉 Baseline training complete! The 'iso_forest.pkl' model has been updated.")

if __name__ == "__main__":
    # Ensure this folder exists and has your clean engine sounds
    TRAINING_DIR = "healthy_audio_samples"
    
    if not os.path.exists(TRAINING_DIR):
        os.makedirs(TRAINING_DIR)
        print(f"Created folder '{TRAINING_DIR}'. Please put your healthy .wav files in here and run again.")
    else:
        train_real_baseline(TRAINING_DIR)