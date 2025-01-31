from datetime import datetime
from typing import Optional, List
import uuid

from pydantic import BaseModel, EmailStr
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, Relationship, SQLModel

Base = declarative_base()


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner")


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: int


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    title: str = Field(min_length=1, max_length=255)


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: int | None = Field(default=None, foreign_key="user.id", nullable=False)
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: int
    owner_id: int


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: int | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


class Agents(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    ap_id = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    configuration = Column(JSON)
    onboard = Column(Boolean, default=False)
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
    timestamp = Column(DateTime,
                       default=datetime.utcnow)  # Automatically sets the timestamp when the command is created
    status = Column(String, nullable=False, default="pending")  # Tracks the command status (pending, completed, etc.)
    agent = relationship("Agents", back_populates="commands")

    def __repr__(self):
        return f"<Command(agent_id={self.agent_id}, command={self.command}, timestamp={self.timestamp})>"


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


class AgentTokenData(BaseModel):
    ap_id: str
    onboard: bool
    scopes: List[str] = []

    class Config:
        orm_mode = True


# Pydantic Model for Command
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


# Define the schema for a single emulator configuration
class EmulatorConfig(BaseModel):
    access_point_type: str
    num_access_points: int
    locations: List[str]
    num_devices: int
    duration: int


# Define the schema for multiple emulators in a single request
class MultiEmulatorRequest(BaseModel):
    emulators: List[EmulatorConfig]


# Add the class configuration for Pydantic models to support ORMs
for model in [UserCreate, UserUpdate, AgentCreate, AgentUpdate, ThirdPartyAppCreate, ThirdPartyAppUpdate]:
    model.Config = type('Config', (), {"orm_mode": True})
