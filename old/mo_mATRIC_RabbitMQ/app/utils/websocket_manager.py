from fastapi import WebSocket
from typing import Dict

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, job_number: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[job_number] = websocket

    async def disconnect(self, job_number: str):
        if job_number in self.active_connections:
            websocket = self.active_connections.pop(job_number)
            await websocket.close()

    async def send_message(self, job_number: str, message: dict):
        if job_number in self.active_connections:
            websocket = self.active_connections[job_number]
            await websocket.send_json(message)

    def is_connected(self, job_number: str) -> bool:
        return job_number in self.active_connections