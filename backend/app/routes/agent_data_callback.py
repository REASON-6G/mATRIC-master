# /routes/agent_data_callback.py

from fastapi import APIRouter, WebSocket, HTTPException, Body
from typing import Dict, List
from app.utils.websocket_manager import WebSocketManager

router = APIRouter()

# This dictionary keeps track of active WebSocket connections by job_number
active_connections: Dict[str, WebSocket] = {}

# Initialize WebSocketManager
ws_manager = WebSocketManager()


# WebSocket endpoint for clients to connect and receive data
@router.websocket("/ws/{job_number}")
async def websocket_endpoint(websocket: WebSocket, job_number: str):
    """
    WebSocket endpoint for third-party apps to connect.
    Each connection is identified by a unique job_number.
    """
    await ws_manager.connect(job_number, websocket)
    active_connections[job_number] = websocket

    try:
        while True:
            # Keep connection open and listen for incoming data
            await websocket.receive_text()
    except Exception as e:
        print(f"WebSocket connection closed for job_number {job_number}: {str(e)}")
    finally:
        await ws_manager.disconnect(job_number)


# HTTP callback endpoint to receive agent data from the subscriber
@router.post("")
async def agent_data_callback(job_number: str, data: List = Body(...),):
    """
    Callback endpoint to receive agent data from the subscriber.
    The data will be sent to the WebSocket client identified by the job_number.
    """
    # Check if the job_number exists in active connections
    if job_number not in active_connections:
        raise HTTPException(status_code=404, detail="WebSocket connection not found for this job_number")

    # Send the agent data to the WebSocket client
    websocket = active_connections[job_number]
    try:
        await ws_manager.send_message(websocket, data)
        return {"status": "success", "detail": f"Data sent for job_number {job_number}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send data: {str(e)}")
