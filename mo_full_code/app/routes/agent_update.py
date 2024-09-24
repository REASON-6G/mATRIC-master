from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import Dict
from app.dependencies import get_db
from app.auth import get_current_agent
from app.models import AgentTokenData
from app.wiremq.mapp_publisher import MAppPublisher

router = APIRouter()

# Initialize the publisher
mapp_publisher = MAppPublisher()

@router.post("/update", response_model=dict)
async def update_agent(
    data: Dict,
    db: Session = Depends(get_db),
    current_agent: AgentTokenData = Depends(get_current_agent)
):
        # Check if the agent is onboard
        print("current_agent.onboard: ", current_agent.onboard)
        if not current_agent.onboard:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Agent is not onboarded"
            )

        ap_id = data.get("ap_id")
        print("ap_id2: ", ap_id)
        payload = data.get("payload")
        print("payload2: ", payload)

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
            # Use a dynamic topic based on the agent ID
            topic = f"agent/{ap_id}/data"
            print("topic: ", topic)

            # Publish data using the MAppPublisher
            mapp_publisher.publish_data(topic, payload)

            return {"status": "success", "detail": f"Data published to topic {topic}"}

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
