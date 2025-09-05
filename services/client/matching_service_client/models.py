from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str]
    role: str
    created_at: datetime

class Topic(BaseModel):
    id: str
    topic: str
    description: Optional[str]
    created_at: datetime

class Subscription(BaseModel):
    id: str
    user_id: str
    topic_filter: str
    queue: Optional[str]
    active: bool
    created_at: datetime
    updated_at: Optional[datetime]

class Publisher(BaseModel):
    id: str
    name: str
    description: Optional[str]
    organisation: Optional[str]
    location: Optional[dict]
    created_at: datetime

class Metric(BaseModel):
    id: str
    topic: str
    value: float
    unit: Optional[str]
    timestamp: datetime

class MatchResult(BaseModel):
    subscription_id: str
    user_id: str
    filter: str

class MatchResponse(BaseModel):
    topic: str
    matches: List[MatchResult]
