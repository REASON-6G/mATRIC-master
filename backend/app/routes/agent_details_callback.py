# /routes/agent_details_callback.py

from __future__ import annotations
import asyncio
from typing import Dict, List
from fastapi import APIRouter, WebSocket, HTTPException, Body
from starlette.websockets import WebSocketDisconnect
from app.utils.websocket_manager import WebSocketManager

router = APIRouter()
active_connections: Dict[str, WebSocket] = {}
ws_manager = WebSocketManager()

@router.websocket("/ws/{job_number}")
async def websocket_endpoint(websocket: WebSocket, job_number: str):
    await websocket.accept()

    # IMPORTANT: connect must NOT call websocket.accept() or websocket.close()
    await ws_manager.connect(job_number, websocket)
    active_connections[job_number] = websocket

    try:
        # Keep the connection alive forever; do not require client frames
        while True:
            await asyncio.sleep(30)
    except WebSocketDisconnect:
        pass
    except Exception:
        # log if you want
        pass
    finally:
        active_connections.pop(job_number, None)
        # IMPORTANT: let the server’s close sequence finish; don’t close twice
        await ws_manager.disconnect(job_number)

@router.post("")
async def agent_details_callback(
    job_number: str,
    agent_details: List[Dict] = Body(...),
):
    if not isinstance(agent_details, list):
        raise HTTPException(status_code=400, detail="Agent details must be a list of dictionaries")

    if not ws_manager.is_connected(job_number):
        raise HTTPException(status_code=404, detail="WebSocket connection not found for this job_number")

    try:
        await ws_manager.send_message(job_number, agent_details)
        return {"status": "success", "job_number": job_number, "data": agent_details}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send data: {str(e)}")
