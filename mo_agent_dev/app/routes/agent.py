from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..auth import get_current_user, auth_manager
from ..models import AgentConfiguration, AgentUpdate, Agent, TokenData, AgentCreate
from ..database import DatabaseManager
from ..dependencies import get_db

router = APIRouter()

@router.post("/public", response_model=Agent)
async def create_first_agent(user: AgentCreate, db: Session = Depends(get_db)):
    db_manager = DatabaseManager(db)
    existing_agent = db_manager.get_agent_by_username(user.ap_id)
    if existing_agent:
        raise HTTPException(status_code=400, detail="username already registered")
    password_hash = auth_manager.hash_password(user.password)
    new_agent = db_manager.add_agent(user.ap_id, password_hash, user.configuration)
    if not new_agent:
        raise HTTPException(status_code=400, detail="user creation failed")
    return new_agent


@router.post("/", response_model=Agent)
async def create_agent(agent: AgentCreate, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    if 'admin' not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create agents")
    db_manager = DatabaseManager(db)
    existing_agent = db_manager.get_agent_by_username(agent.ap_id)
    if existing_agent:
        raise HTTPException(status_code=400, detail="username already registered")
    password_hash = auth_manager.hash_password(agent.password)
    new_agent = db_manager.add_agent(agent.ap_id, password_hash, agent.configuration)
    if not new_agent:
        raise HTTPException(status_code=400, detail="Agent creation failed")
    return new_agent

@router.get("/{ap_id}", response_model=Agent)
async def get_agent(ap_id: str, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    db_manager = DatabaseManager(db)
    agent = db_manager.get_agent(ap_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.put("/{ap_id}", response_model=Agent)
async def update_agent(ap_id: str, agent: AgentUpdate, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    if 'admin' not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update agents")
    db_manager = DatabaseManager(db)
    updated_agent = db_manager.update_agent(ap_id, agent.configuration)
    if not updated_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return updated_agent

@router.delete("/{ap_id}", response_model=dict)
async def delete_agent(ap_id: str, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    if 'admin' not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete agents")
    db_manager = DatabaseManager(db)
    success = db_manager.delete_agent(ap_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"status": "success", "detail": f"Agent {ap_id} deleted"}
