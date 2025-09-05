import asyncio
from typing import Optional, Callable, List
from datetime import datetime
import httpx
from pydantic import BaseModel, Field


# -------------------------------
# Models
# -------------------------------
class AuthResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None

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


# -------------------------------
# API Client
# -------------------------------
class MatchingServiceClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.client = httpx.AsyncClient(timeout=10.0)

    # ---------------------------
    # Auth
    # ---------------------------
    async def login(self, username: str, password: str):
        resp = await self.client.post(f"{self.base_url}/api/auth/login",
                                      json={"username": username, "password": password})
        resp.raise_for_status()
        data = AuthResponse(**resp.json())
        self.access_token = data.access_token
        self.refresh_token = data.refresh_token

    def _headers(self):
        if not self.access_token:
            raise RuntimeError("Not authenticated")
        return {"Authorization": f"Bearer {self.access_token}"}

    # ---------------------------
    # Users
    # ---------------------------
    async def list_users(self) -> List[User]:
        resp = await self.client.get(f"{self.base_url}/api/users", headers=self._headers())
        resp.raise_for_status()
        return [User(**u) for u in resp.json()]

    async def get_user(self, user_id: str) -> User:
        resp = await self.client.get(f"{self.base_url}/api/users/{user_id}", headers=self._headers())
        resp.raise_for_status()
        return User(**resp.json())

    async def create_user(self, username: str, email: str, password: str,
                          full_name: Optional[str] = None, role: str = "user"):
        payload = {"username": username, "email": email, "password": password,
                   "full_name": full_name, "role": role}
        resp = await self.client.post(f"{self.base_url}/api/users", json=payload, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    async def update_user(self, user_id: str, **kwargs):
        resp = await self.client.put(f"{self.base_url}/api/users/{user_id}", json=kwargs, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    async def delete_user(self, user_id: str):
        resp = await self.client.delete(f"{self.base_url}/api/users/{user_id}", headers=self._headers())
        resp.raise_for_status()
        return resp.status_code

    # ---------------------------
    # Topics
    # ---------------------------
    async def list_topics(self) -> List[Topic]:
        resp = await self.client.get(f"{self.base_url}/api/topics", headers=self._headers())
        resp.raise_for_status()
        return [Topic(**t) for t in resp.json()]

    async def get_topic(self, topic_id: str) -> Topic:
        resp = await self.client.get(f"{self.base_url}/api/topics/{topic_id}", headers=self._headers())
        resp.raise_for_status()
        return Topic(**resp.json())

    async def create_topic(self, topic: str, description: Optional[str] = None):
        payload = {"topic": topic, "description": description}
        resp = await self.client.post(f"{self.base_url}/api/topics", json=payload, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    async def update_topic(self, topic_id: str, **kwargs):
        resp = await self.client.put(f"{self.base_url}/api/topics/{topic_id}", json=kwargs, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    async def delete_topic(self, topic_id: str):
        resp = await self.client.delete(f"{self.base_url}/api/topics/{topic_id}", headers=self._headers())
        resp.raise_for_status()
        return resp.status_code

    # ---------------------------
    # Subscriptions
    # ---------------------------
    async def list_subscriptions(self) -> List[Subscription]:
        resp = await self.client.get(f"{self.base_url}/api/subscriptions", headers=self._headers())
        resp.raise_for_status()
        return [Subscription(**s) for s in resp.json()]

    async def get_subscription(self, sub_id: str) -> Subscription:
        resp = await self.client.get(f"{self.base_url}/api/subscriptions/{sub_id}", headers=self._headers())
        resp.raise_for_status()
        return Subscription(**resp.json())

    async def create_subscription(self, topic_filter: str, queue: Optional[str] = None):
        payload = {"topic_filter": topic_filter, "queue": queue}
        resp = await self.client.post(f"{self.base_url}/api/subscriptions", json=payload, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    async def update_subscription(self, sub_id: str, **kwargs):
        resp = await self.client.put(f"{self.base_url}/api/subscriptions/{sub_id}", json=kwargs, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    async def delete_subscription(self, sub_id: str):
        resp = await self.client.delete(f"{self.base_url}/api/subscriptions/{sub_id}", headers=self._headers())
        resp.raise_for_status()
        return resp.status_code

    # ---------------------------
    # Publishers
    # ---------------------------
    async def list_publishers(self) -> List[Publisher]:
        resp = await self.client.get(f"{self.base_url}/api/publishers", headers=self._headers())
        resp.raise_for_status()
        return [Publisher(**p) for p in resp.json()]

    async def get_publisher(self, pub_id: str) -> Publisher:
        resp = await self.client.get(f"{self.base_url}/api/publishers/{pub_id}", headers=self._headers())
        resp.raise_for_status()
        return Publisher(**resp.json())

    async def create_publisher(self, name: str, description: Optional[str] = None,
                               organisation: Optional[str] = None, location: Optional[dict] = None):
        payload = {"name": name, "description": description, "organisation": organisation, "location": location}
        resp = await self.client.post(f"{self.base_url}/api/publishers", json=payload, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    async def update_publisher(self, pub_id: str, **kwargs):
        resp = await self.client.put(f"{self.base_url}/api/publishers/{pub_id}", json=kwargs, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    async def delete_publisher(self, pub_id: str):
        resp = await self.client.delete(f"{self.base_url}/api/publishers/{pub_id}", headers=self._headers())
        resp.raise_for_status()
        return resp.status_code

    # ---------------------------
    # Metrics
    # ---------------------------
    async def list_metrics(self) -> List[Metric]:
        resp = await self.client.get(f"{self.base_url}/api/metrics", headers=self._headers())
        resp.raise_for_status()
        return [Metric(**m) for m in resp.json()]

    async def get_metric(self, metric_id: str) -> Metric:
        resp = await self.client.get(f"{self.base_url}/api/metrics/{metric_id}", headers=self._headers())
        resp.raise_for_status()
        return Metric(**resp.json())

    async def create_metric(self, topic: str, value: float, unit: Optional[str] = None):
        payload = {"topic": topic, "value": value, "unit": unit}
        resp = await self.client.post(f"{self.base_url}/api/metrics", json=payload, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    async def metrics_stats(self):
        resp = await self.client.get(f"{self.base_url}/api/metrics/stats", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    # ---------------------------
    # Match API
    # ---------------------------
    async def test_match(self, topic: str) -> MatchResponse:
        payload = {"topic": topic}
        resp = await self.client.post(f"{self.base_url}/api/match/test", json=payload, headers=self._headers())
        resp.raise_for_status()
        return MatchResponse(**resp.json())

    async def list_match_subscriptions(self) -> List[MatchResult]:
        resp = await self.client.get(f"{self.base_url}/api/match/subscriptions", headers=self._headers())
        resp.raise_for_status()
        return [MatchResult(**s) for s in resp.json()]

    # ---------------------------
    # RabbitMQ
    # ---------------------------
    async def publish(self, topic: str, payload: dict):
        resp = await self.client.post(f"{self.base_url}/api/queues/publish",
                                      json={"topic": topic, "payload": payload},
                                      headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    async def subscribe(self, topic_filter: str) -> str:
        resp = await self.client.post(f"{self.base_url}/api/queues/subscribe",
                                      json={"filter": topic_filter},
                                      headers=self._headers())
        resp.raise_for_status()
        return resp.json()["queue"]

    async def poll(self, queue: str) -> Optional[dict]:
        resp = await self.client.post(f"{self.base_url}/api/queues/poll",
                                      json={"queue": queue}, headers=self._headers())
        resp.raise_for_status()
        msg = resp.json()
        return msg.get("message")

    def async_subscribe(self, queue: str, callback: Callable[[dict], None], interval: float = 0.5):
        async def poll_loop():
            while True:
                msg = await self.poll(queue)
                if msg:
                    callback(msg)
                await asyncio.sleep(interval)

        return asyncio.create_task(poll_loop())

    async def close(self):
        await self.client.aclose()
