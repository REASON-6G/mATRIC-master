# /routes/agent_details_callback.py

from fastapi import APIRouter, WebSocket, HTTPException, Body, Request
from typing import Dict, List
from app.utils.websocket_manager import WebSocketManager


router = APIRouter()

# This dictionary will keep track of active WebSocket connections by job_number
active_connections: Dict[str, WebSocket] = {}

# Initialize WebSocketManager
ws_manager = WebSocketManager()


# WebSocket endpoint for third-party apps to connect and receive data
@router.websocket("/ws/{job_number}")
async def websocket_endpoint(websocket: WebSocket, job_number: str):
    """
    WebSocket endpoint that third-party apps connect to.
    Each connection is identified by a unique job_number.
    """
    await websocket.accept()
    await ws_manager.connect(job_number, websocket)
    active_connections[job_number] = websocket

    try:
        while True:
            # Keep connection open and listen for data (if needed)
            await websocket.receive_text()
    except Exception as e:
        print(f"WebSocket connection closed for job_number {job_number}: {str(e)}")
    finally:
        await ws_manager.disconnect(job_number)
        # active_connections.pop(job_number, None)


# HTTP callback endpoint to receive agent details from the subscriber
@router.post("")
async def agent_details_callback(job_number: str, agent_details: List[Dict] = Body(...),):
    """
    Callback endpoint to receive agent details from the subscriber.
    The agent details will be sent to the WebSocket client identified by the job_number.
    """
    # Check if the job_number exists in active connections
    print(f"job_number: {job_number}")
    print(f"agent_details: {agent_details}")
    if not isinstance(agent_details, list):
        raise HTTPException(status_code=400, detail="Agent details must be a list of dictionaries")

    if not ws_manager.is_connected(job_number):
        raise HTTPException(status_code=404, detail="WebSocket connection not found for this job_number")

    try:
        await ws_manager.send_message(job_number, agent_details)
        return {"status": "success", "job_number": job_number, "data": agent_details, "detail": f"Data sent for job_number {job_number}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send data: {str(e)}")

    # return {"status": "success", "job_number": job_number, "data": agent_details}



    # print("data: ", data)
    # if job_number not in active_connections:
    #     raise HTTPException(status_code=404, detail="WebSocket connection not found for this job_number")
    #
    # # Send the agent details to the WebSocket client
    # websocket = active_connections[job_number]
    # try:
    #     await ws_manager.send_message(websocket, data)
    #     return {"status": "success", "detail": f"Data sent for job_number {job_number}"}
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Failed to send data: {str(e)}")
