# /routes/agent_details.py

from fastapi import APIRouter, HTTPException, Depends
from app.wiremq.agent_task_publisher import AgentTaskPublisher  # Updated import
from app.auth import get_current_user, get_current_third_party_app  # Authentication dependencies
import uuid

router = APIRouter()

# Endpoint to request details for all agents, only for authenticated users and third-party apps
@router.post("/request_all_agents_details")
async def request_all_agents_details(
    # current_user=Depends(get_current_user),  # For authenticated users
    # current_third_party=Depends(get_current_third_party_app)  # For authenticated third-party apps
):
    """
    Endpoint to request details for all agents.
    Only authenticated users and third-party apps can access this.
    """
    try:
        # Step 1: Generate a unique job_number for this request
        job_number = str(uuid.uuid4())
        print("job_number: ", job_number)

        # Step 2: Use the AgentTaskPublisher to publish the request to WireMQ
        print("before publisher init")
        publisher = AgentTaskPublisher()
        print("before publish")
        publisher.publish_agent_task(job_number, task_type="all_agents_details")
        print("after publish")

        # Step 3: Return the job_number to the third-party app or user
        return {"job_number": job_number}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error requesting agent details: {str(e)}")
