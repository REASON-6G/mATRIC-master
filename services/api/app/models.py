from datetime import datetime, timezone
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

#
# USER
#
class User(BaseModel):
    id: Optional[str] = Field(alias="_id")
    username: str
    email: str
    role: str = "user"  # "user" | "admin"
    password_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

#
# SUBSCRIBER
#
class Subscription(BaseModel):
    id: Optional[str] = Field(alias="_id")
    user_id: str  # references User
    topic_filter: str  # e.g. "uk/bristol/*/*/*/attenuation/*"
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

#
# PUBLISHER
#
class Publisher(BaseModel):
    id: Optional[str] = Field(alias="_id")
    name: str
    user_id: str  # owner
    topics: List[str] = []  # exact topics this publisher can publish to
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    location: Dict[str, Any]

#
# TOPIC
#
class Topic(BaseModel):
    id: Optional[str] = Field(alias="_id")
    topic: str  # full encoded name
    publisher_id: Optional[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

#
# METRIC (for Influx, reference only in Mongo)
#
class Metric(BaseModel):
    id: Optional[str] = Field(alias="_id")
    topic: str
    field: str
    value_type: str  # float | int | str
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

#
# SERVICE STATE / CONFIG
#
class ServiceState(BaseModel):
    id: Optional[str] = Field(alias="_id")
    name: str
    config: dict
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
