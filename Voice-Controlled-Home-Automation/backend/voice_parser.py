import os
import sys
import json
import pyaudio
import requests
from vosk import Model, KaldiRecognizer

# Ensure you have a 'model' folder with the downloaded Vosk model
MODEL_PATH = "model"
API_URL = "http://localhost:8000/command"

if not os.path.exists(MODEL_PATH):
    print("Please download a Vosk model and unpack as 'model' in the current folder.")
    sys.exit(1)

model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, 16000)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()

print("Listening for commands... (Try: 'turn on living room light' or 'turn off bedroom fan')")

def parse_and_execute(text):
    text = text.lower()
    state = None
    device_id = None

    # Simple NLP logic
    if "turn on" in text:
        state = True
    elif "turn off" in text:
        state = False

    if "living room" in text and "light" in text:
        device_id = "lr_light_1"
    elif "bedroom" in text and "nightstand" in text:
        device_id = "bd_light_1"
    elif "living room" in text and "fan" in text:
        device_id = "lr_fan_1"

    if state is not None and device_id:
        print(f"Executing: Device {device_id} -> {'ON' if state else 'OFF'}")
        requests.post(f"{API_URL}?device_id={device_id}&state={str(state).lower()}")

while True:
    data = stream.read(4000, exception_on_overflow=False)
    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        text = result.get("text", "")
        if text:
            print(f"Recognized: {text}")
            parse_and_execute(text)