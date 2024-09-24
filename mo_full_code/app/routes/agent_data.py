# /routes/agent_data.py

from fastapi import APIRouter, HTTPException, Depends
from app.wiremq.agent_task_publisher import AgentTaskPublisher
from app.auth import get_current_user, get_current_agent  # Authentication dependencies
import uuid
from datetime import datetime

router = APIRouter()

# Endpoint to request agent data for a specific period, accessible by authenticated users and agents
@router.post("/request_agent_data")
async def request_agent_data(
    agent_id: str,
    start_time: datetime,
    end_time: datetime,
):
    """
    Endpoint to request agent data for a specific period.
    Both authenticated agents and users can request agent data.
    """
    try:
        # Step 1: Generate a unique job_number for this request
        job_number = str(uuid.uuid4())
        print("job_number: ", job_number)

        # Step 2: Use the AgentTaskPublisher to publish the request to WireMQ
        publisher = AgentTaskPublisher()
        task_data = {
            "agent_id": agent_id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        print("task_data: ", task_data)
        publisher.publish_agent_task(job_number, task_type="agent_data", additional_data=task_data)

        # Step 3: Return the job_number to the requester
        return {"job_number": job_number}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error requesting agent data: {str(e)}")
