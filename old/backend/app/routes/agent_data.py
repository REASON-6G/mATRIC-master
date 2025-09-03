# /routes/agent_data.py

from fastapi import APIRouter, HTTPException, Depends
from app.rabbitmq.rabbitmq_publisher import RabbitMQPublisher
from app.auth import get_authenticated_user_or_app  # Unified authentication dependency
import uuid
from datetime import datetime

router = APIRouter()

# Initialize the RabbitMQ publisher
publisher = RabbitMQPublisher()

@router.post("/request_agent_data")
async def request_agent_data(
    agent_id: str,
    start_time: datetime,
    end_time: datetime,
    authenticated_entity=Depends(get_authenticated_user_or_app)
):
    """
    Endpoint to request agent data for a specific period.
    Both authenticated agents and users can request agent data.
    """
    try:
        # Step 1: Generate a unique job_number for this request
        job_number = str(uuid.uuid4())

        # Step 2: Construct the task data
        task_data = {
            "job_number": job_number,
            "task_type": "agent_data",
            "data": {
                "agent_id": agent_id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
            },
        }

        # Step 3: Publish the task to RabbitMQ
        publisher.publish(
            routing_key="agent_data",
            message=task_data,
        )

        # Step 4: Return the job_number to the requester
        return {"job_number": job_number}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error requesting agent data: {str(e)}")
