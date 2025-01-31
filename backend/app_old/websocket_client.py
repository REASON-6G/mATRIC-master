import websockets
import asyncio

async def receive_agent_details(job_number: str):
    async with websockets.connect(f"ws://127.0.0.1:8000/ws/{job_number}") as websocket:
        while True:
            data = await websocket.recv()
            print(f"Received data: {data}")

# Run the WebSocket client
job_number = "c3510906-58f7-42af-9cb3-85c24f71689c"
asyncio.get_event_loop().run_until_complete(receive_agent_details(job_number))