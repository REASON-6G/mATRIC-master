from sqlalchemy import Column, String, JSON, ForeignKey, Boolean, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from pydantic import BaseModel, EmailStr
from typing import Optional, List

Base = declarative_base()


# SQLAlchemy Models
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    roles = Column(String, nullable=False)
    # roles = relationship("Role", secondary=user_roles, back_populates="users")

    def __repr__(self):
        return f"<User(username={self.username}, roles={self.roles})>"

class Agents(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    ap_id = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    configuration = Column(JSON)
    onboard = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Agent(ap_id={self.ap_id}, onboard={self.onboard})>"

class ThirdPartyApps(Base):
    __tablename__ = "third_party_apps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    app_name = Column(String, unique=True, index=True, nullable=False)
    api_key = Column(String, nullable=False)
    permissions = Column(JSON, nullable=False)

    def __repr__(self):
        return f"<ThirdPartyApp(app_name={self.app_name})>"


# Pydantic Models
class UserCreate(BaseModel):
    username: EmailStr
    password: str
    roles: List[str]

class UserUpdate(BaseModel):
    password: Optional[str] = None
    roles: Optional[List[str]] = None


class AgentCreate(BaseModel):
    ap_id: str
    password: str
    configuration: dict

class AgentConfiguration(BaseModel):
    ap_id: str
    configuration: dict
    supported_commands: Optional[List[str]] = None

class AgentUpdate(BaseModel):
    password: Optional[str] = None
    configuration: Optional[dict] = None

class Agent(BaseModel):
    id: uuid.UUID
    ap_id: str
    configuration: dict

    class Config:
        orm_mode = True


class ThirdPartyAppCreate(BaseModel):
    app_name: str
    api_key: str
    permissions: dict

class ThirdPartyAppUpdate(BaseModel):
    api_key: Optional[str] = None
    permissions: Optional[dict] = None

class ThirdPartyApp(BaseModel):
    id: uuid.UUID
    app_name: str
    api_key: str
    permissions: dict

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class TokenData(BaseModel):
    username: Optional[str] = None
    roles: str
    scopes: List[str] = []

    class Config:
        orm_mode = True

# Add the class configuration for Pydantic models to support ORMs
for model in [UserCreate, UserUpdate, AgentCreate, AgentUpdate, ThirdPartyAppCreate, ThirdPartyAppUpdate]:
    model.Config = type('Config', (), {"orm_mode": True})
