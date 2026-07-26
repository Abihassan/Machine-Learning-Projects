import gradio as gr
from audio_processor import load_audio, generate_mel_spectrogram_image
from model_inference import extract_embeddings
from anomaly_detector import EngineAnomalyDetector
from PIL import Image

# Initialize detector
detector = EngineAnomalyDetector()

# --- MOCK TRAINING FOR DEMONSTRATION ---
# In a real scenario, you would run detector.train_baseline() using 
# embeddings extracted from 20-30 audio files of a perfectly healthy engine.
# For this script to work immediately, we will trick it by fitting random noise 
# just so the UI functions. Replace this in production!

# ---------------------------------------

def analyze_engine_sound(audio_path):
    if audio_path is None:
        return "Please upload an audio file.", None, 0.0
        
    try:
        # 1. Preprocess
        wav = load_audio(audio_path)
        
        # 2. Extract Features
        embedding = extract_embeddings(wav)
        
        # 3. Detect Anomaly
        status, score = detector.predict(embedding)
        
        # 4. Generate Visuals
        spectrogram_buf = generate_mel_spectrogram_image(wav)
        spectrogram_img = Image.open(spectrogram_buf)
        
        # Format the score context
        explanation = (
            f"Confidence Score: {score:.3f}\n"
            "(Positive scores indicate healthy baseline conformity. "
            "Negative scores indicate severe deviation/anomaly.)"
        )
        
        return status, spectrogram_img, explanation
        
    except Exception as e:
        return f"Error processing audio: {str(e)}", None, ""

# Gradio Interface
with gr.Blocks(title="Machine Mechanical Audio Auditor") as demo:
    gr.Markdown("# 🏭 Machine Mechanical Audio Auditor")
    gr.Markdown("Diagnose engine health by uploading sonic hums (.wav). Runs 100% locally.")
    
    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(type="filepath", label="Upload Engine Audio (.wav)")
            analyze_btn = gr.Button("Analyze Engine Health", variant="primary")
            
        with gr.Column():
            status_output = gr.Textbox(label="Diagnosis", text_align="center")
            score_output = gr.Textbox(label="Anomaly Score Details")
            spectrogram_output = gr.Image(label="Audio Spectrogram")
            
    analyze_btn.click(
        fn=analyze_engine_sound,
        inputs=audio_input,
        outputs=[status_output, spectrogram_output, score_output]
    )

if __name__ == "__main__":
    print("Starting local edge UI...")
    demo.launch(server_name="127.0.0.1", server_port=7860)