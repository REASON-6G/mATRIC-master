# /routes/send_command.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.wiremq.agent_task_publisher import AgentTaskPublisher
from app.auth import get_current_third_party_app  # Authentication for third-party apps
from app.utils.conflict_resolution_layer import ConflictResolutionLayer  # Conflict resolution layer
from app.database import get_db_manager  # Get DatabaseManager dependency
import uuid

router = APIRouter()

# Create an instance of ConflictResolutionLayer
conflict_layer = ConflictResolutionLayer()

# Endpoint to send a command to a specific agent, accessible only by authenticated third-party apps
@router.post("")
async def send_command_to_agent(
    agent_id: str,
    command: str,
    db_manager=Depends(get_db_manager),  # Inject the DatabaseManager dependency
):
    """
    Endpoint to send a command to a specific agent.
    Only authenticated third-party apps can send commands.
    """
    try:
        # Step 1: Retrieve the agent's configuration from the database
        agent = db_manager.get_agent(agent_id)
        print("agent: ", agent)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

        # Retrieve the commands field
        available_commands = agent.configuration.get("commands", [])
        print("available_commands: ", available_commands)
        if not available_commands:
            raise HTTPException(status_code=400, detail=f"Agent {agent_id} has no commands configured")

        # Step 2: Check if the command is in the agent's list of commands
        if command not in available_commands:
            raise HTTPException(status_code=400, detail=f"Command '{command}' is not supported by agent {agent_id}")

        # Step 3: Generate a unique job_number for this request
        job_number = str(uuid.uuid4())
        print("job_number: ", job_number)

        # Step 4: Check if there has been a recent command for the agent using the conflict resolution layer
        # if not conflict_layer.is_command_allowed(agent_id, db_manager):
        #     raise HTTPException(status_code=409, detail=f"Command for agent {agent_id} was recently sent. New command discarded.")
        #
        # # Step 5: Register the new command in the conflict resolution layer (and save to the database)
        # conflict_layer.register_command(agent_id, command, db_manager)

        # Step 6: Use the AgentTaskPublisher to publish the command task to WireMQ
        publisher = AgentTaskPublisher()
        task_data = {
            "agent_id": agent_id,
            "command": command
        }
        print("task_data: ", task_data)
        publisher.publish_agent_task(job_number, task_type="send_command", additional_data=task_data)

        # Step 7: Return the job_number to the requester
        return {"job_number": job_number}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending command to agent: {str(e)}")
