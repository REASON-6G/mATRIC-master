from fastapi import APIRouter, WebSocket, HTTPException, Body
from typing import Dict
from app.utils.websocket_manager import WebSocketManager

router = APIRouter()

# Initialize WebSocketManager
ws_manager = WebSocketManager()

# WebSocket endpoint for clients to connect and receive emulator task updates
@router.websocket("/ws/{job_number}")
async def websocket_endpoint(websocket: WebSocket, job_number: str):
    """
    WebSocket endpoint for clients to connect and receive emulator task updates.
    Each connection is identified by a unique job_number.
    """
    await ws_manager.connect(job_number, websocket)

    try:
        while True:
            # Keep connection alive (optional: listen for incoming messages)
            await websocket.receive_text()
    except Exception as e:
        print(f"WebSocket connection closed for job_number {job_number}: {str(e)}")
    finally:
        await ws_manager.disconnect(job_number)


# HTTP callback endpoint to receive emulator task completion updates
@router.post("/callback/emulator")
async def emulator_callback(job_number: str, status: str, details: Dict = Body(...)):
    """
    Callback endpoint to receive emulator task completion updates from the subscriber.
    The status and details will be sent to the WebSocket client identified by job_number.
    """
    # Check if the job_number has an active WebSocket connection
    if not ws_manager.is_connected(job_number):
        raise HTTPException(status_code=404, detail="WebSocket connection not found for this job_number")

    # Prepare the message payload
    payload = {
        "job_number": job_number,
        "status": status,
        "details": details
    }

    # Send the emulator task update to the WebSocket client
    try:
        await ws_manager.send_message(job_number, payload)
        return {"status": "success", "detail": f"Emulator task update sent for job_number {job_number}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send update: {str(e)}")
