from sqlalchemy import Column, String, JSON, ForeignKey, Boolean, Table, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime

Base = declarative_base()


# SQLAlchemy Models
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    roles = Column(String, nullable=False)

    def __repr__(self):
        return f"<User(username={self.username}, roles={self.roles})>"


class Agents(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    ap_id = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    configuration = Column(JSON)
    onboard = Column(Boolean, default=False)
    emulator_started_at = Column(DateTime(timezone=True), nullable=True, index=True)
    commands = relationship("AgentCommand", back_populates="agent")

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


# Command Model
class AgentCommand(Base):
    __tablename__ = "commands"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    agent_id = Column(String, ForeignKey("agents.ap_id"), nullable=False)  # Foreign key to Agents table
    command = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False, default="pending")
    agent = relationship("Agents", back_populates="commands")

    def __repr__(self):
        return f"<Command(agent_id={self.agent_id}, command={self.command}, timestamp={self.timestamp})>"


# ---------------- Pydantic Models ----------------

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


class AgentTokenData(BaseModel):
    ap_id: str
    onboard: bool
    scopes: List[str] = []

    class Config:
        orm_mode = True


class CommandCreate(BaseModel):
    agent_id: uuid.UUID
    command: str


class CommandResponse(BaseModel):
    id: uuid.UUID
    agent_id: uuid.UUID
    command: str
    timestamp: datetime
    status: str

    class Config:
        orm_mode = True


class EmulatorConfig(BaseModel):
    access_point_type: str
    num_access_points: int
    locations: List[str]
    num_devices: int
    duration: int


class MultiEmulatorRequest(BaseModel):
    emulators: List[EmulatorConfig]


# Emulator API request models (Pydantic v2)
class EmulatorSpec(BaseModel):
    access_point_type: str = Field(..., pattern=r"^(5G|WiFi|LiFi)$")
    num_access_points: int = Field(..., gt=0, le=1000)
    # Accepts place names (e.g. "Leeds") OR "lat,lon" strings. We’ll normalise to coordinates.
    locations: List[str]
    num_devices: int = Field(..., gt=0)
    duration: int = Field(..., gt=0)  # minutes


class EmulatorSpinupRequest(BaseModel):
    emulators: List[EmulatorSpec]

    @field_validator("emulators")
    @classmethod
    def not_empty(cls, v):
        if not v:
            raise ValueError("emulators must not be empty")
        return v


# Keep legacy v1-style orm_mode setup (harmless warning in v2)
for model in [UserCreate, UserUpdate, AgentCreate, AgentUpdate, ThirdPartyAppCreate, ThirdPartyAppUpdate]:
    model.Config = type("Config", (), {"orm_mode": True})


class AgentSummary(BaseModel):
    id: str
    name: Optional[str] = None


class AgentPoint(BaseModel):
    ts: str  # ISO-8601 timestamp
    value: float


class AgentSeries(BaseModel):
    agent_id: str
    points: List[AgentPoint] = []
