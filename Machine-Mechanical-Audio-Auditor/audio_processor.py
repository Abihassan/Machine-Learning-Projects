import librosa
import numpy as np
import matplotlib.pyplot as plt
import io
import noisereduce as nr

def load_audio(file_path, target_sr=16000, apply_noise_reduction=True):
    """Loads audio, converts to mono, resamples, and optionally reduces background noise."""
    wav, sr = librosa.load(file_path, sr=target_sr, mono=True)
    
    if apply_noise_reduction:
        # Perform spectral gating noise reduction
        # We use the first 0.5 seconds of the audio as the noise profile baseline
        # (Assuming the engine hum is constant, this filters out non-stationary background hiss)
        wav = nr.reduce_noise(y=wav, sr=sr, stationary=True)
        
    return wav

# ... (keep generate_mel_spectrogram_image exactly the same as before)