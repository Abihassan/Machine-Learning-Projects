"""
Module D: Streamlit Dashboard
Provides a web UI for the Quality Control Scanner. Displays live video,
tracks pass/fail metrics, and allows exporting logs.
"""

import streamlit as st
import cv2
import pandas as pd
import time
from datetime import datetime
import os
import sys

# Ensure the 'src' directory is in the system path so we can import our modules
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from src.scanner import QualityControlScanner

# --- 1. Streamlit Page Configuration ---
st.set_page_config(page_title="Factory QC Dashboard", page_icon="🏭", layout="wide")

# --- 2. Session State Initialization ---
# We use session state to remember variables across UI refreshes
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
    st.header("⚙️ Controls")
    
    # Target class configuration for the pre-trained model
    target_object = st.selectbox("Select Target Object (PASS condition)", 
                                 ["cell phone", "bottle", "cup", "mouse", "apple"], 
                                 index=0)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Start", use_container_width=True):
            st.session_state.run_camera = True
    with col2:
        if st.button("⏹️ Stop", use_container_width=True):
            st.session_state.run_camera = False

    st.markdown("---")
    st.header("📊 Live Metrics")
    
    # Calculate defect percentage
    total = st.session_state.metrics["scanned"]
    fails = st.session_state.metrics["fail"]
    defect_rate = (fails / total * 100) if total > 0 else 0.0

    # Display Metrics
    st.metric(label="Total Scanned", value=total)
    st.metric(label="Total Pass ✅", value=st.session_state.metrics["pass"])
    st.metric(label="Total Defective ❌", value=fails)
    st.metric(label="Defect Rate", value=f"{defect_rate:.2f}%")

    st.markdown("---")
    st.header("💾 Export Data")
    # Convert dataframe to CSV for download
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

# Placeholder for the video feed
video_placeholder = st.empty()

# --- 5. Main Video Processing Loop ---
if st.session_state.run_camera:
    # Initialize the scanner (from Module B) with the UI-selected target
    # Lowered confidence slightly to make demo testing easier
    scanner = QualityControlScanner(target_class=target_object, conf_threshold=0.4)
    
    # Open Webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        st.error("Error: Could not access the camera. Check your hardware connection.")
        st.session_state.run_camera = False
    
    while st.session_state.run_camera:
        ret, frame = cap.read()
        if not ret:
            st.error("Error: Failed to grab a frame from the camera.")
            break

        # Process the frame through YOLOv8
        processed_frame, status, confidence = scanner.process_frame(frame)
        
        # --- Factory Line Cooldown Logic ---
        # Only log a new item if 3 seconds have passed since the last scan 
        # AND we actually detect an object in the frame (status is not "NO_OBJECT")
        current_time = time.time()
        if status != "NO_OBJECT" and (current_time - st.session_state.last_scan_time > 3.0):
            st.session_state.metrics["scanned"] += 1
            if status == "PASS":
                st.session_state.metrics["pass"] += 1
            elif status == "FAIL":
                st.session_state.metrics["fail"] += 1
            
            # Log the data
            new_log = pd.DataFrame([{
                "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "Status": status,
                "Confidence": f"{confidence:.2f}"
            }])
            st.session_state.log_data = pd.concat([st.session_state.log_data, new_log], ignore_index=True)
            
            # Reset cooldown timer
            st.session_state.last_scan_time = current_time

        # Convert the OpenCV frame (BGR) to Streamlit format (RGB)
        frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
        
        # Update the UI placeholder with the new frame
        video_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)

    # Release the camera when the loop stops
    cap.release()
else:
    # Show a placeholder image or message when camera is off
    video_placeholder.info("Camera is offline. Click '▶️ Start' in the sidebar to begin inspection.")