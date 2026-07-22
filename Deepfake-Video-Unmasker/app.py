import streamlit as st
import tempfile
import os
import matplotlib.pyplot as plt
from inference import analyze_video

st.set_page_config(page_title="Deepfake Video Unmasker", layout="wide")

st.title("🕵️ Deepfake Video Unmasker (Powered by Pre-Trained AI)")
st.subheader("Frame-by-Frame Temporal Consistency Checker")

st.markdown("""
This tool uses a state-of-the-art pre-trained Vision model from Hugging Face to analyze videos. 
It plots the "Deepfake Probability" across the video's timeline. Authentic videos remain consistently low, 
while deepfakes exhibit high probability spikes or consistent artifacting.
""")

uploaded_file = st.file_uploader("Upload a video (.mp4, .avi, .mov)", type=["mp4", "avi", "mov"])

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    tfile.write(uploaded_file.read())
    video_path = tfile.name
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.video(video_path)
    
    with col2:
        st.write("### Analysis Progress")
        with st.spinner('Loading pre-trained AI and analyzing frames... (This may take a moment on the first run)'):
            scores, frame_indices, overall_score, verdict = analyze_video(video_path)
            
        if not scores:
            st.error(verdict)
        else:
            st.success("Analysis Complete!")
            
            # Display Final Verdict
            if verdict == "Fake":
                st.error(f"**Final Verdict: DEEPFAKE DETECTED** (Confidence: {overall_score:.2f})")
            else:
                st.success(f"**Final Verdict: AUTHENTIC** (Confidence: {1 - overall_score:.2f})")
            
            # Plot Temporal Consistency Graph
            st.write("### Deepfake Probability Timeline")
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(frame_indices, scores, marker='o', linestyle='-', color='r' if verdict=="Fake" else 'g')
            ax.axhline(y=0.6, color='gray', linestyle='--', label='Fake Threshold')
            ax.set_xlabel("Video Frame Number")
            ax.set_ylabel("Fake Probability (0.0 to 1.0)")
            ax.set_ylim(0, 1.1)
            ax.grid(True, linestyle=':', alpha=0.6)
            ax.legend()
            st.pyplot(fig)
            
            st.info("💡 **How to read the graph:** Peaks above the dotted threshold line indicate specific frames in the video where the AI detected deepfake artifacts. A jagged, spiky line indicates temporal inconsistency.")

    os.remove(video_path)