# /routes/agent_details.py

from fastapi import APIRouter, HTTPException, Depends
from app.rabbitmq.rabbitmq_publisher import RabbitMQPublisher
from app.auth import get_authenticated_user_or_app  # Unified authentication
import uuid
import logging

router = APIRouter()

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize RabbitMQPublisher for agent details
rabbitmq_publisher = RabbitMQPublisher()


@router.post("/request_all_agents_details")
async def request_all_agents_details(authenticated_entity=Depends(get_authenticated_user_or_app)):
    """
    Endpoint to request details for all agents.
    Only authenticated users and third-party apps can access this.
    """
    try:
        # Step 1: Generate a unique job_number for this request
        job_number = str(uuid.uuid4())
        logger.info(f"Generated job_number: {job_number}")

        # Step 2: Prepare the task data
        task_data = {
            "job_number": job_number,
            "task_type": "all_agents_details"
        }

        # Step 3: Publish the task to RabbitMQ
        rabbitmq_publisher.publish("agent_details", task_data)
        logger.info(f"Published task to RabbitMQ: {task_data}")

        # Step 4: Return the job_number to the requester
        return {"job_number": job_number}

    except Exception as e:
        logger.error(f"Error requesting agent details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error requesting agent details: {str(e)}")
