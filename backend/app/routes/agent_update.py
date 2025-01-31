# /routes/agent_update.py

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Dict
from app.dependencies import get_db
from app.auth import get_current_agent
from app.models import AgentTokenData
from app.rabbitmq.rabbitmq_publisher import RabbitMQPublisher  # Import RabbitMQPublisher
import logging

router = APIRouter()

# Initialize RabbitMQ Publisher
rabbitmq_publisher = RabbitMQPublisher()

@router.post("/update", response_model=dict)
async def update_agent(
    data: Dict,
    db: Session = Depends(get_db),
    current_agent: AgentTokenData = Depends(get_current_agent)
):
    """
    Endpoint to handle agent updates.
    """
    # Check if the agent is onboard
    if not current_agent.onboard:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent is not onboarded"
        )

    ap_id = data.get("ap_id")
    print("agent_update ap_id: ", ap_id)
    payload = data.get("payload")
    print("agent_update payload: ", payload)

    if not ap_id or not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid data format"
        )

    # Ensure the ap_id in the data matches the authenticated agent's id
    if ap_id != current_agent.ap_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent ID mismatch"
        )

    try:
        # Publish the update to RabbitMQ
        queue_name = f"agent_update"
        print("agent_update queue_name: ", queue_name)
        rabbitmq_publisher.publish(
            routing_key="agent_update",
            message={"ap_id": ap_id, "payload": payload}
        )
        print("agent_update after publisher: ")
        return {"status": "success", "detail": f"Data published to queue {queue_name}"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
