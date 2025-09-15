import logging
import asyncio
from typing import Optional, Callable, List, Awaitable, Union
from datetime import datetime, timezone
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
    name: str
    api_token: str
    description: Optional[str] = None
    organisation: Optional[str] = None
    location: Optional[dict] = Field(
        None, example={"type": "Point", "coordinates": [-2.58791, 51.4545]}
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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

class Emulator(BaseModel):
    owner_id: str
    publisher_id: str
    name: str
    topic: str
    msg_schema: dict
    interval: float = 5.0
    running: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


# -------------------------------
# API Client
# -------------------------------
class MatchingServiceClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.client = httpx.AsyncClient(timeout=10.0)
        self._lock = asyncio.Lock()
    
    async def _request(
        self,
        method: str,
        path: str,
        **kwargs
    ) -> httpx.Response:
        """
        Perform an HTTP request with automatic token refresh on 401.
        """
        url = f"{self.base_url}{path}"
        headers = kwargs.pop("headers", {})
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        resp = await self.client.request(method, url, headers=headers, **kwargs)

        # If unauthorized, attempt refresh
        if resp.status_code == 401 and self.refresh_token:
            async with self._lock:
                # Double-check if another coroutine has refreshed
                if headers.get("Authorization") != f"Bearer {self.access_token}":
                    headers["Authorization"] = f"Bearer {self.access_token}"
                    resp = await self.client.request(method, url, headers=headers, **kwargs)
                else:
                    await self.refresh()
                    headers["Authorization"] = f"Bearer {self.access_token}"
                    resp = await self.client.request(method, url, headers=headers, **kwargs)

        await raise_for_status_with_logging(resp)
        return resp

    # ---------------------------
    # Auth
    # ---------------------------
    async def login(self, username: str, password: str):
        resp = await self._request("POST", "/api/auth/login", json={"username": username, "password": password})
        data = AuthResponse(**resp.json())
        self.access_token = data.access_token
        self.refresh_token = data.refresh_token

    async def login_with_token(self, api_token: str):
        """
        Authenticates using a publisher API token.
        Exchanges it for a short-lived JWT + refresh token.
        """
        resp = await self._request("POST", "/api/auth/validate", json={"api_token": api_token})
        data = AuthResponse(**resp.json())
        self.access_token = data.access_token
        self.refresh_token = data.refresh_token
        return data

    async def refresh(self):
        """
        Refresh the access token using the refresh token.
        """
        if not self.refresh_token:
            raise RuntimeError("No refresh token available")

        resp = await self.client.post(
            f"{self.base_url}/api/auth/refresh",
            headers={"Authorization": f"Bearer {self.refresh_token}"}
        )
        await raise_for_status_with_logging(resp)
        self.access_token = resp.json()["access_token"]

    def _headers(self):
        if not self.access_token:
            raise RuntimeError("Not authenticated")
        return {"Authorization": f"Bearer {self.access_token}"}
    
    # ---------------------------
    # Teardown
    # ---------------------------
    
    async def close(self):
        """
        Close the underlying HTTP client session.
        """
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

    # ---------------------------
    # Public HTTP methods
    # ---------------------------
    async def get(self, path: str, **kwargs):
        return await self._request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs):
        return await self._request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs):
        return await self._request("PUT", path, **kwargs)

    async def delete(self, path: str, **kwargs):
        return await self._request("DELETE", path, **kwargs)

    # ---------------------------
    # Users
    # ---------------------------
    async def list_users(self) -> List[User]:
        resp = await self.get("/api/users")
        return [User(**u) for u in resp.json()]

    async def get_user(self, user_id: str) -> User:
        resp = await self.get(f"/api/users/{user_id}")
        return User(**resp.json())

    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        role: str = "user"
    ):
        payload = {
            "username": username,
            "email": email,
            "password": password,
            "full_name": full_name,
            "role": role
        }
        resp = await self.post("/api/users", json=payload)
        return resp.json()

    async def update_user(self, user_id: str, **kwargs):
        resp = await self.put(f"/api/users/{user_id}", json=kwargs)
        return resp.json()

    async def delete_user(self, user_id: str):
        resp = await self.delete(f"/api/users/{user_id}")
        return resp.status_code

    # ---------------------------
    # Topics
    # ---------------------------
    async def list_topics(self) -> List[Topic]:
        resp = await self.client.get(f"{self.base_url}/api/topics/", headers=self._headers())
        await raise_for_status_with_logging(resp)
        return [Topic(**t) for t in resp.json()]
    
    async def list_my_topics(self) -> List[Topic]:
        resp = await self.client.get(f"{self.base_url}/api/topics/mine", headers=self._headers())
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
        resp = await self.get("/api/subscriptions/")
        return [Subscription(**s) for s in resp.json()]

    async def get_subscription(self, sub_id: str) -> Subscription:
        resp = await self.get(f"/api/subscriptions/{sub_id}")
        return Subscription(**resp.json())

    async def create_subscription(self, topic_filter: str, queue: Optional[str] = None):
        payload = {"topic_filter": topic_filter}
        if queue:
            payload["queue"] = queue
        try:
            resp = await self.post("/api/subscriptions/", json=payload)
            return Subscription(**resp.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409:
                self.logger.warning(f"Subscription for '{topic_filter}' already exists")
                return {"warning": "Subscription already exists", "topic_filter": topic_filter}
            raise

    async def update_subscription(self, sub_id: str, **kwargs):
        resp = await self.put(f"/api/subscriptions/{sub_id}", json=kwargs)
        return Subscription(**resp.json())

    async def delete_subscription(self, sub_id: str):
        resp = await self.delete(f"/api/subscriptions/{sub_id}")
        return resp.status_code

    # ---------------------------
    # Publishers
    # ---------------------------
    async def list_publishers(self) -> List[Publisher]:
        resp = await self.get("/api/publishers/")
        return [Publisher(**p) for p in resp.json()]

    async def get_publisher(self, pub_id: str) -> Publisher:
        resp = await self.get(f"/api/publishers/{pub_id}")
        return Publisher(**resp.json())

    async def create_publisher(
        self,
        name: str,
        description: Optional[str] = None,
        organisation: Optional[str] = None,
        location: Optional[dict] = None,
    ):
        payload = {"name": name, "description": description, "organisation": organisation, "location": location}
        try:
            resp = await self.post("/api/publishers/", json=payload)
            return Publisher(**resp.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409:  # duplicate publisher
                self.logger.warning(f"Publisher '{name}' already exists")
                return {"warning": "Publisher already exists", "name": name}
            raise

    async def update_publisher(self, pub_id: str, **kwargs):
        resp = await self.put(f"/api/publishers/{pub_id}", json=kwargs)
        return Publisher(**resp.json())

    async def delete_publisher(self, pub_id: str):
        resp = await self.delete(f"/api/publishers/{pub_id}")
        return resp.status_code

    # ---------------------------
    # Metrics
    # ---------------------------
    async def list_metrics(self) -> List[Metric]:
        resp = await self.get("/api/metrics/")
        return [Metric(**m) for m in resp.json()]

    # ---------------------------
    # Match API
    # ---------------------------
    async def test_match(self, topic: str) -> MatchResponse:
        payload = {"topic": topic}
        resp = await self.post("/api/match/test", json=payload)
        return MatchResponse(**resp.json())

    async def list_match_subscriptions(self) -> List[MatchResult]:
        resp = await self.get("/api/match/subscriptions")
        return [MatchResult(**s) for s in resp.json()]

    # ---------------------------
    # RabbitMQ
    # ---------------------------
    async def publish(self, topic: str, payload: dict):
        """
        Publish a message to a topic.
        Ensures a durable queue exists for the topic in the exchange.
        """
        resp = await self.post("/api/queues/publish", json={"topic": topic, "payload": payload})
        return resp.json()

    async def subscribe(self, topic_filter: str) -> dict:
        """
        Subscribe to a topic filter (supports wildcards).
        Returns subscription ID, queue name, and filter.
        """
        resp = await self.post("/api/queues/subscribe", json={"filter": topic_filter})
        return resp.json()

    async def poll(self, queue: str) -> Optional[dict]:
        """
        Poll a queue for messages (non-blocking).
        Returns None if no message is available.
        """
        resp = await self.post("/api/queues/poll", json={"queue": queue})
        msg = resp.json()
        return msg.get("message")

    def async_poll(
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


    # ---------------------------
    # Emulators
    # ---------------------------

    async def list_emulators(self) -> List[Emulator]:
        """List all emulators visible to the current user"""
        resp = await self.get("/api/emulators/")
        return [Emulator(**e) for e in resp.json()]

    async def create_emulator(self, name: str, topic: str, schema: dict, interval: float) -> Emulator:
        """Create a new emulator"""
        payload = {"name": name, "topic": topic, "msg_schema": schema, "interval": interval}
        resp = await self.post("/api/emulators/", json=payload)
        return Emulator(**resp.json())

    async def get_emulator(self, emulator_id: str) -> Emulator:
        """Fetch a single emulator by ID"""
        resp = await self.get(f"/api/emulators/{emulator_id}")
        return Emulator(**resp.json())

    async def update_emulator(
        self, emulator_id: str, name: Optional[str] = None, topic: Optional[str] = None,
        schema: Optional[dict] = None, interval: Optional[float] = None
    ) -> Emulator:
        """Update emulator fields"""
        payload = {}
        if name is not None:
            payload["name"] = name
        if topic is not None:
            payload["topic"] = topic
        if schema is not None:
            payload["msg_schema"] = schema
        if interval is not None:
            payload["interval"] = interval

        if not payload:
            raise ValueError("No fields provided for update")

        resp = await self.put(f"/api/emulators/{emulator_id}", json=payload)
        return Emulator(**resp.json())

    async def delete_emulator(self, emulator_id: str) -> dict:
        """Delete an emulator"""
        resp = await self.delete(f"/api/emulators/{emulator_id}")
        return resp.json()    

    async def start_emulator(self, emulator_id: str) -> Emulator:
        """Set an emulator's 'running' attribute to True"""
        payload = {
            "running": True
        }

        resp = await self.put(f"/api/emulators/{emulator_id}", json=payload)
        return Emulator(**resp.json())

    async def stop_emulator(self, emulator_id: str) -> Emulator:
        """Set an emulator's 'running' attribute to False"""
        payload = {
            "running": False
        }

        resp = await self.put(f"/api/emulators/{emulator_id}", json=payload)
        return Emulator(**resp.json())
