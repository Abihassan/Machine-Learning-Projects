from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import json
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock Database
db_state = {
    "living_room": [
        {"id": "lr_light_1", "name": "Main Light", "type": "light", "state": False, "value": 100},
        {"id": "lr_fan_1", "name": "Ceiling Fan", "type": "fan", "state": False, "value": 3}
    ],
    "bedroom": [
        {"id": "bd_light_1", "name": "Nightstand", "type": "light", "state": True, "value": 50},
        {"id": "bd_ac_1", "name": "Thermostat", "type": "ac", "state": False, "value": 22}
    ]
}

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Send initial state
        await websocket.send_json({"type": "INIT_STATE", "data": db_state})

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle manual frontend overrides here if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/rooms")
def get_rooms():
    return db_state

@app.post("/command")
async def process_command(device_id: str, state: bool):
    """Update device state and broadcast to UI"""
    for room, devices in db_state.items():
        for device in devices:
            if device["id"] == device_id:
                device["state"] = state
                await manager.broadcast({"type": "STATE_UPDATE", "data": db_state})
                return {"status": "success", "device": device}
    return {"status": "error", "message": "Device not found"}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)