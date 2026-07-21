"""
Module D: Streamlit Dashboard
Provides a web UI for the Quality Control Scanner. Supports live webcam
and uploaded sample videos.
"""

import streamlit as st
import cv2
import pandas as pd
import time
from datetime import datetime
import os
import sys

# Ensure the 'src' directory is in the system path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from src.scanner import QualityControlScanner

# --- 1. Streamlit Page Configuration ---
st.set_page_config(page_title="Factory QC Dashboard", page_icon="🏭", layout="wide")

# --- 2. Session State Initialization ---
if 'run_camera' not in st.session_state:
    st.session_state.run_camera = False
if 'metrics' not in st.session_state:
    st.session_state.metrics = {"scanned": 0, "pass": 0, "fail": 0}
if 'log_data' not in st.session_state:
    st.session_state.log_data = pd.DataFrame(columns=["Timestamp", "Status", "Confidence"])
if 'last_scan_time' not in st.session_state:
    st.session_state.last_scan_time = 0.0

# --- 3. Sidebar UI (Controls & Metrics) ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Input Source Selection
    input_source = st.radio("Select Video Source", ["Webcam", "Video File"])
    
    video_path = 0  # Default to webcam ID 0
    if input_source == "Video File":
        uploaded_file = st.file_uploader("Upload Sample Video", type=["mp4", "avi", "mov"])
        if uploaded_file is not None:
            # Save the uploaded file temporarily so OpenCV can read it
            video_path = "temp_sample_video.mp4"
            with open(video_path, "wb") as f:
                f.write(uploaded_file.read())
            st.success("Video uploaded successfully!")
        else:
            video_path = None # Prevents starting if no file is uploaded

    # Target class configuration
    target_object = st.selectbox("Select Target Object (PASS condition)", 
                                 ["cell phone", "bottle", "cup", "mouse", "apple"], 
                                 index=0)
    
    st.markdown("---")
    st.header("▶️ Controls")
    col1, col2 = st.columns(2)
    with col1:
        # Disable start button if video file is selected but not yet uploaded
        can_start = video_path is not None
        if st.button("Start", use_container_width=True, disabled=not can_start):
            st.session_state.run_camera = True
    with col2:
        if st.button("Stop", use_container_width=True):
            st.session_state.run_camera = False

    st.markdown("---")
    st.header("📊 Live Metrics")
    
    total = st.session_state.metrics["scanned"]
    fails = st.session_state.metrics["fail"]
    defect_rate = (fails / total * 100) if total > 0 else 0.0

    st.metric(label="Total Scanned", value=total)
    st.metric(label="Total Pass ✅", value=st.session_state.metrics["pass"])
    st.metric(label="Total Defective ❌", value=fails)
    st.metric(label="Defect Rate", value=f"{defect_rate:.2f}%")

    st.markdown("---")
    st.header("💾 Export Data")
    csv = st.session_state.log_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Daily Log (CSV)",
        data=csv,
        file_name=f"qc_log_{datetime.now().strftime('%Y-%m-%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

    if st.button("🗑️ Reset Metrics"):
        st.session_state.metrics = {"scanned": 0, "pass": 0, "fail": 0}
        st.session_state.log_data = pd.DataFrame(columns=["Timestamp", "Status", "Confidence"])
        st.rerun()

# --- 4. Main Dashboard UI ---
st.title("🏭 Product Quality Control Scanner")
st.markdown("Real-time automated sorting using YOLOv8 computer vision.")

video_placeholder = st.empty()

# --- 5. Main Video Processing Loop ---
if st.session_state.run_camera and video_path is not None:
    scanner = QualityControlScanner(target_class=target_object, conf_threshold=0.4)
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        st.error("Error: Could not read the video source.")
        st.session_state.run_camera = False
    
    while st.session_state.run_camera:
        ret, frame = cap.read()
        if not ret:
            st.success("✅ Video processing complete.")
            st.session_state.run_camera = False
            break

        processed_frame, status, confidence = scanner.process_frame(frame)
        
        # Factory Line Cooldown Logic
        current_time = time.time()
        if status != "NO_OBJECT" and (current_time - st.session_state.last_scan_time > 3.0):
            st.session_state.metrics["scanned"] += 1
            if status == "PASS":
                st.session_state.metrics["pass"] += 1
            elif status == "FAIL":
                st.session_state.metrics["fail"] += 1
            
            new_log = pd.DataFrame([{
                "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "Status": status,
                "Confidence": f"{confidence:.2f}"
            }])
            st.session_state.log_data = pd.concat([st.session_state.log_data, new_log], ignore_index=True)
            st.session_state.last_scan_time = current_time

        frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        video_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)
        
        # Add a tiny sleep to prevent recorded videos from playing back at 1000 FPS
        if input_source == "Video File":
            time.sleep(0.03) 

    cap.release()
else:
    video_placeholder.info("System is idle. Select your input source and click 'Start' in the sidebar.")