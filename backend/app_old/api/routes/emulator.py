# /routes/emulator.py

from fastapi import APIRouter, HTTPException
from app.rabbitmq.rabbitmq_publisher import RabbitMQPublisher
import uuid

router = APIRouter()
# Initialize the RabbitMQ publisher
publisher = RabbitMQPublisher()

@router.post("/spinup")
async def spinup_emulators(task_data: dict):
    """
    Endpoint to spin up emulators.
    """
    # Generate a unique job_number for the task
    job_number = str(uuid.uuid4())
    task_data["job_number"] = job_number

    try:
        # Publish the task to RabbitMQ
        publisher.publish(routing_key="emulator_spinup", message=task_data)

        # Return the job_number to the requester
        return {"status": "success", "job_number": job_number}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to publish task: {e}")
