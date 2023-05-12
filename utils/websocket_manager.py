from typing import List, Dict
from fastapi import WebSocket, WebSocketDisconnect


class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, plant_id: str):
        await websocket.accept()
        if plant_id in self.active_connections:
            self.active_connections[plant_id].append(websocket)
        else:
            self.active_connections[plant_id] = [websocket]

    def disconnect(self, websocket: WebSocket, plant_id: str):
        if plant_id in self.active_connections:
            self.active_connections[plant_id].remove(websocket)
            if not self.active_connections[plant_id]:
                del self.active_connections[plant_id]

    async def send_message(self, message: str, plant_id: str):
        if plant_id in self.active_connections:
            for websocket in self.active_connections[plant_id]:
                await websocket.send_text(message)
