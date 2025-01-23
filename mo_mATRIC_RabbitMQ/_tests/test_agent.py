import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.models import Agent, TokenData
from app.dependencies import get_db
from app.auth import get_current_user
import uuid

client = TestClient(app)

class FakeDatabaseManager:
    def __init__(self):
        self.agents = {}

    def get_agent_by_username(self, username):
        return self.agents.get(username)

    def add_agent(self, ap_id, password_hash, configuration):
        agent_id = uuid.uuid4()
        agent = Agent(
            id=agent_id,
            ap_id=ap_id,
            password_hash=password_hash,
            configuration=configuration
        )
        self.agents[ap_id] = agent
        return agent

def override_get_db():
    db = FakeDatabaseManager()
    try:
        yield db
    finally:
        pass

def override_get_current_user():
    return TokenData(username="admin", roles="admin", scopes=[])

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.fixture
def auth_manager_mock():
    with patch('app.auth.auth_manager') as mock:
        yield mock

def test_create_agent(auth_manager_mock):
    agent_data = {
        "ap_id": "test_ap_id",
        "password": "test_password",
        "configuration": {"key": "value"}
    }
    password_hash = "hashed_test_password"

    auth_manager_instance = auth_manager_mock.return_value
    auth_manager_instance.hash_password.return_value = password_hash

    token = "fake_token"
    auth_manager_instance.create_access_token.return_value = token

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = client.post("/agents/", json=agent_data, headers=headers)

    print("Test - Response status code:", response.status_code)
    print("Test - Response content:", response.json())
    assert response.status_code == 200
    assert response.json()["ap_id"] == agent_data["ap_id"]

