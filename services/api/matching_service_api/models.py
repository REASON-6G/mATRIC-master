from pydantic import BaseModel, Field, constr, EmailStr
from typing import Optional, Literal, List
from datetime import datetime, timezone
from bson import ObjectId

from matching_service_api.utils import mongo_client


# -------------------
# Helpers
# -------------------
def mongo_to_dict(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable dict."""
    if not doc:
        return {}
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            doc[k] = str(v)
        elif isinstance(v, datetime):
            doc[k] = v.isoformat()
    return doc


# -------------------
# Core Models (DB)
# -------------------
class UserModel(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    role: Literal["user", "agent", "admin"] = "user"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TopicModel(BaseModel):
    topic: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SubscriptionModel(BaseModel):
    user_id: str
    topic_filter: str
    queue: Optional[str] = None
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


class PublisherModel(BaseModel):
    name: str
    description: Optional[str] = None
    organisation: Optional[str] = None
    location: Optional[dict] = Field(
        None, example={"type": "Point", "coordinates": [-2.58791, 51.4545]}
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MetricModel(BaseModel):
    topic: str  # changed from 'name' to 'topic' to match API
    value: float
    unit: Optional[str] = None
    timestamp: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

# --- Match Models ---
class MatchRequest(BaseModel):
    topic: str


class MatchResult(BaseModel):
    subscription_id: str
    user_id: str
    filter: str


class MatchResponse(BaseModel):
    topic: str
    matches: List[MatchResult]

# -------------------
# Response Models (API)
# -------------------
class UserResponse(UserModel):
    id: str


class TopicResponse(TopicModel):
    id: str


class SubscriptionResponse(SubscriptionModel):
    id: str


class PublisherResponse(PublisherModel):
    id: str


class MetricResponse(BaseModel):
    id: str
    topic: str
    value: float
    unit: Optional[str] = None
    timestamp: datetime


# -------------------
# Indexes
# -------------------
try:
    mongo_client.db.topics.create_index("topic", unique=True)
    mongo_client.db.users.create_index("username", unique=True)
    mongo_client.db.users.create_index("email", unique=True)
    mongo_client.db.publishers.create_index("name", unique=True)
except Exception:
    pass  # ignore if already exists
