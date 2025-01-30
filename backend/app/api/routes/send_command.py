from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.rabbitmq.rabbitmq_publisher import RabbitMQPublisher
from app.utils.conflict_resolution_layer import ConflictResolutionLayer  # Conflict resolution layer
from app.database import get_db_manager  # Get DatabaseManager dependency
import uuid

router = APIRouter()

# Create an instance of ConflictResolutionLayer
conflict_layer = ConflictResolutionLayer()

# Initialize RabbitMQ Publisher
publisher = RabbitMQPublisher()

@router.post("")
async def send_command_to_agent(
    agent_id: str,
    command: str,
    db_manager=Depends(get_db_manager),
):
    """
    Endpoint to send a command to a specific agent.
    """
    try:
        # Step 1: Retrieve the agent's configuration from the database
        agent = db_manager.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

        # Retrieve the commands field
        available_commands = agent.configuration.get("commands", [])
        if not available_commands:
            raise HTTPException(status_code=400, detail=f"Agent {agent_id} has no commands configured")

        # Step 2: Check if the command is in the agent's list of commands
        if command not in available_commands:
            raise HTTPException(status_code=400, detail=f"Command '{command}' is not supported by agent {agent_id}")

        # Step 3: Generate a unique job_number for this request
        job_number = str(uuid.uuid4())

        # Step 4: Check if there has been a recent command for the agent using the conflict resolution layer
        if not conflict_layer.is_command_allowed(agent_id, db_manager):
            raise HTTPException(
                status_code=409, detail=f"Command for agent {agent_id} was recently sent. New command discarded."
            )

        # Step 5: Register the new command in the conflict resolution layer (and save to the database)
        conflict_layer.register_command(agent_id, command, db_manager)

        # Step 6: Publish the command task to RabbitMQ
        task_data = {
            "job_number": job_number,
            "agent_id": agent_id,
            "command": command,
        }
        publisher.publish("send_command", task_data)

        # Step 7: Return the job_number to the requester
        return {"job_number": job_number}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending command to agent: {str(e)}")
