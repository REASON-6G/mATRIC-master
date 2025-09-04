from pydantic import BaseModel, Field, constr, conlist
from typing import Optional, List
from datetime import datetime

class UserModel(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: constr(min_length=5, max_length=100)
    full_name: Optional[str] = None
    role: Optional[str] = "user"  # e.g., user/admin
    created_at: Optional[datetime] = None

class TopicModel(BaseModel):
    topic: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None

class SubscriptionModel(BaseModel):
    user_id: str
    topic_filter: str  # e.g., "uk/bristol/*/*/*/attenuation/*"
    active: bool = True
    created_at: Optional[datetime] = None

class PublisherModel(BaseModel):
    name: str
    organisation: Optional[str] = None
    location: Optional[dict] = Field(
        None, example={"type": "Point", "coordinates": [-2.58791, 51.4545]}
    )  # GeoJSON format
    created_at: Optional[datetime] = None

class MetricModel(BaseModel):
    topic: str
    value: float
    unit: Optional[str] = None
    timestamp: Optional[datetime] = None
