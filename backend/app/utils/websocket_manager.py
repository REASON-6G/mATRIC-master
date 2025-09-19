from typing import Dict
from fastapi import WebSocket

class WebSocketManager:
    def __init__(self) -> None:
        # job_number -> websocket
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, job_number: str, websocket: WebSocket) -> None:
        """
        Register a websocket for a job_number.
        NOTE: Do NOT call websocket.accept() here; the route should have already accepted.
        """
        # If a previous socket exists for the same job, drop it silently
        old = self.active_connections.get(job_number)
        if old is not None and old is not websocket:
            # Don't close here; the route owning 'old' will handle teardown
            self.active_connections.pop(job_number, None)

        self.active_connections[job_number] = websocket

    async def disconnect(self, job_number: str) -> None:
        """
        Unregister a websocket by job_number.
        NOTE: Do NOT call websocket.close() here; the route will close during its own teardown.
        """
        self.active_connections.pop(job_number, None)

    async def send_message(self, job_number: str, message: dict) -> None:
        """
        Send a JSON message to the websocket associated with job_number.
        If the socket is gone/closed, remove it.
        """
        ws = self.active_connections.get(job_number)
        if not ws:
            raise RuntimeError(f"No active websocket for job_number: {job_number}")

        try:
            await ws.send_json(message)
        except Exception:
            # Socket likely closed/reset; unregister it
            self.active_connections.pop(job_number, None)
            raise

    def is_connected(self, job_number: str) -> bool:
        return job_number in self.active_connections
