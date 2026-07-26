import tensorflow as tf
import tensorflow_hub as hub
import numpy as np

# Load YAMNet from TF Hub (Downloads once and caches locally)
YAMNET_MODEL_URL = 'https://tfhub.dev/google/yamnet/1'
print("Loading YAMNet model... This may take a moment on first run.")
yamnet_model = hub.load(YAMNET_MODEL_URL)

def extract_embeddings(wav_data):
    """
    Passes audio through YAMNet and returns the averaged embedding.
    YAMNet expects waveform values in the [-1.0, +1.0] range.
    """
    # YAMNet outputs: scores, embeddings, spectrogram
    scores, embeddings, spectrogram = yamnet_model(wav_data)
    
    # The embeddings are shape (N, 1024) where N is the number of 0.96s frames.
    # We average them to get a single (1024,) vector representing the whole file.
    avg_embedding = np.mean(embeddings.numpy(), axis=0)
    
    return avg_embedding