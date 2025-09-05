import logging
import asyncio
from typing import Optional, Callable, List, Awaitable, Union
from datetime import datetime
from pydantic import BaseModel, Field
import httpx
from httpx import HTTPStatusError


async def raise_for_status_with_logging(resp: httpx.Response):
    if resp.is_error:
        try:
            # Try to get JSON first
            error_content = resp.json()
        except Exception:
            # Fall back to text
            error_content = resp.text
        logging.error(
            "HTTP %s error for %s: %s",
            resp.status_code,
            resp.url,
            error_content,
        )
        resp.raise_for_status()


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
        await raise_for_status_with_logging(resp)
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
        await raise_for_status_with_logging(resp)
        return [User(**u) for u in resp.json()]

    async def get_user(self, user_id: str) -> User:
        resp = await self.client.get(f"{self.base_url}/api/users/{user_id}", headers=self._headers())
        await raise_for_status_with_logging(resp)
        return User(**resp.json())

    async def create_user(self, username: str, email: str, password: str,
                          full_name: Optional[str] = None, role: str = "user"):
        payload = {"username": username, "email": email, "password": password,
                   "full_name": full_name, "role": role}
        resp = await self.client.post(f"{self.base_url}/api/users", json=payload, headers=self._headers())
        await raise_for_status_with_logging(resp)
        return resp.json()

    async def update_user(self, user_id: str, **kwargs):
        resp = await self.client.put(f"{self.base_url}/api/users/{user_id}", json=kwargs, headers=self._headers())
        await raise_for_status_with_logging(resp)
        return resp.json()

    async def delete_user(self, user_id: str):
        resp = await self.client.delete(f"{self.base_url}/api/users/{user_id}", headers=self._headers())
        await raise_for_status_with_logging(resp)
        return resp.status_code

    # ---------------------------
    # Topics
    # ---------------------------
    async def list_topics(self) -> List[Topic]:
        resp = await self.client.get(f"{self.base_url}/api/topics/", headers=self._headers())
        await raise_for_status_with_logging(resp)
        return [Topic(**t) for t in resp.json()]

    async def get_topic(self, topic_id: str) -> Topic:
        resp = await self.client.get(f"{self.base_url}/api/topics/{topic_id}", headers=self._headers())
        await raise_for_status_with_logging(resp)
        return Topic(**resp.json())

    async def create_topic(self, topic: str, description: Optional[str] = None):
        payload = {"topic": topic, "description": description}
        try:
            resp = await self.client.post(
                f"{self.base_url}/api/topics/", json=payload, headers=self._headers()
            )
            await raise_for_status_with_logging(resp)
            return resp.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409:  # duplicate topic
                logging.warning(f"Topic '{topic}' already exists")
                return {"topic": topic, "warning": "Topic already exists", "id": None}
            raise

    async def update_topic(self, topic_id: str, **kwargs):
        resp = await self.client.put(f"{self.base_url}/api/topics/{topic_id}", json=kwargs, headers=self._headers())
        await raise_for_status_with_logging(resp)
        return resp.json()

    async def delete_topic(self, topic_id: str):
        resp = await self.client.delete(f"{self.base_url}/api/topics/{topic_id}", headers=self._headers())
        await raise_for_status_with_logging(resp)
        return resp.status_code

    # ---------------------------
    # Subscriptions
    # ---------------------------
    async def list_subscriptions(self) -> List[Subscription]:
        resp = await self.client.get(f"{self.base_url}/api/subscriptions/", headers=self._headers())
        await raise_for_status_with_logging(resp)
        return [Subscription(**s) for s in resp.json()]

    async def get_subscription(self, sub_id: str) -> Subscription:
        resp = await self.client.get(f"{self.base_url}/api/subscriptions/{sub_id}", headers=self._headers())
        await raise_for_status_with_logging(resp)
        return Subscription(**resp.json())

    async def create_subscription(self, topic_filter: str, queue: Optional[str] = None):
        payload = {"topic_filter": topic_filter, "queue": queue}

        try:
            resp = await self.client.post(
                f"{self.base_url}/api/subscriptions/", json=payload, headers=self._headers()
            )
            await raise_for_status_with_logging(resp)
            return resp.json()
        except HTTPStatusError as e:
            if e.response.status_code == 409:  # duplicate subscription
                self.logger.warning(f"Subscription for '{topic_filter}' already exists")
                return {"warning": "Subscription already exists", "topic_filter": topic_filter}
            raise

    async def update_subscription(self, sub_id: str, **kwargs):
        resp = await self.client.put(f"{self.base_url}/api/subscriptions/{sub_id}", json=kwargs, headers=self._headers())
        await raise_for_status_with_logging(resp)
        return resp.json()

    async def delete_subscription(self, sub_id: str):
        resp = await self.client.delete(f"{self.base_url}/api/subscriptions/{sub_id}", headers=self._headers())
        await raise_for_status_with_logging(resp)
        return resp.status_code

    # ---------------------------
    # Publishers
    # ---------------------------
    async def list_publishers(self) -> List[Publisher]:
        resp = await self.client.get(f"{self.base_url}/api/publishers/", headers=self._headers())
        await raise_for_status_with_logging(resp)
        return [Publisher(**p) for p in resp.json()]

    async def get_publisher(self, pub_id: str) -> Publisher:
        resp = await self.client.get(f"{self.base_url}/api/publishers/{pub_id}", headers=self._headers())
        await raise_for_status_with_logging(resp)
        return Publisher(**resp.json())

    async def create_publisher(
        self,
        name: str,
        description: Optional[str] = None,
        organisation: Optional[str] = None,
        location: Optional[dict] = None,
    ):
        payload = {
            "name": name,
            "description": description,
            "organisation": organisation,
            "location": location,
        }

        try:
            resp = await self.client.post(
                f"{self.base_url}/api/publishers/", json=payload, headers=self._headers()
            )
            await raise_for_status_with_logging(resp)
            return resp.json()
        except HTTPStatusError as e:
            if e.response.status_code == 409:  # duplicate
                self.logger.warning(f"Publisher '{name}' already exists")
                return {"warning": "Publisher already exists", "name": name}
            raise

    async def update_publisher(self, pub_id: str, **kwargs):
        resp = await self.client.put(f"{self.base_url}/api/publishers/{pub_id}", json=kwargs, headers=self._headers())
        await raise_for_status_with_logging(resp)
        return resp.json()

    async def delete_publisher(self, pub_id: str):
        resp = await self.client.delete(f"{self.base_url}/api/publishers/{pub_id}", headers=self._headers())
        await raise_for_status_with_logging(resp)
        return resp.status_code

    # ---------------------------
    # Metrics
    # ---------------------------
    async def list_metrics(self) -> List[Metric]:
        resp = await self.client.get(f"{self.base_url}/api/metrics/", headers=self._headers())
        await raise_for_status_with_logging(resp)
        return [Metric(**m) for m in resp.json()]

    # ---------------------------
    # Match API
    # ---------------------------
    async def test_match(self, topic: str) -> MatchResponse:
        payload = {"topic": topic}
        resp = await self.client.post(f"{self.base_url}/api/match/test", json=payload, headers=self._headers())
        await raise_for_status_with_logging(resp)
        return MatchResponse(**resp.json())

    async def list_match_subscriptions(self) -> List[MatchResult]:
        resp = await self.client.get(f"{self.base_url}/api/match/subscriptions", headers=self._headers())
        await raise_for_status_with_logging(resp)
        return [MatchResult(**s) for s in resp.json()]

    # ---------------------------
    # RabbitMQ
    # ---------------------------
    async def publish(self, topic: str, payload: dict):
        """
        Publish a message to a topic.
        Ensures a durable queue exists for the topic in the exchange.
        """
        resp = await self.client.post(
            f"{self.base_url}/api/queues/publish",
            json={"topic": topic, "payload": payload},
            headers=self._headers()
        )
        await raise_for_status_with_logging(resp)
        return resp.json()

    async def subscribe(self, topic_filter: str) -> str:
        """
        Subscribe to a topic filter (supports wildcards). Returns the queue name.
        """
        # Send the correct JSON key "filter" to match the Flask endpoint
        resp = await self.client.post(
            f"{self.base_url}/api/queues/subscribe",
            json={"filter": topic_filter},
            headers=self._headers()
        )
        await raise_for_status_with_logging(resp)
        data = resp.json()
        return data

    async def poll(self, queue: str) -> Optional[dict]:
        """
        Poll a queue for messages (non-blocking).
        Returns None if no message is available.
        """
        resp = await self.client.post(
            f"{self.base_url}/api/queues/poll",
            json={"queue": queue},
            headers=self._headers()
        )
        await raise_for_status_with_logging(resp)
        msg = resp.json()
        return msg.get("message")

    def async_subscribe(
        self,
        queue: str,
        callback: Union[Callable[[dict], None], Callable[[dict], Awaitable[None]]],
        interval: float = 0.5
    ):
        """
        Background task to poll a queue at regular intervals and call the callback for each message.
        Supports both sync and async callbacks.
        """
        import asyncio, inspect

        async def poll_loop():
            while True:
                msg = await self.poll(queue)
                if msg:
                    if inspect.iscoroutinefunction(callback):
                        await callback(msg)   # await if async function
                    else:
                        callback(msg)         # call directly if sync function
                await asyncio.sleep(interval)

        return asyncio.create_task(poll_loop())

    async def close(self):
        await self.client.aclose()
