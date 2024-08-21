# tests/test_agent.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import Agents, TokenData
from app.auth import get_current_user
from jose import jwt
from unittest.mock import patch
import uuid

# Create a TestClient instance
client = TestClient(app)

# Define application's secret key and algorithm
SECRET_KEY = "f4e26a5290b9762bdbe668c50f9003d14ed9a5dda5c79a53cc188fcb8d64979e"  # Use the same secret key as application
ALGORITHM = "HS256"  # Ensure this matches the algorithm app uses

# Utility function to create a signed JWT
def create_signed_jwt(payload: dict) -> str:
    """Generates a signed JWT using the same secret key and algorithm as the application."""
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Mock function to simulate a user with an admin role
def override_get_current_user():
    """Return a mock TokenData object with admin role."""
    return TokenData(username="admin@example.com", roles="admin", scopes=[])

# Override the get_current_user dependency in the auth module
app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.fixture
def db_manager_mocks():
    """Provide mock implementations of database manager methods."""
    with patch('app.database.DatabaseManager.get_agent_by_username') as get_agent_by_username, \
         patch('app.database.DatabaseManager.add_agent') as add_agent, \
         patch('app.database.DatabaseManager.get_agent') as get_agent, \
         patch('app.database.DatabaseManager.update_agent') as update_agent, \
         patch('app.database.DatabaseManager.delete_agent') as delete_agent:

        yield {
            'get_agent_by_username': get_agent_by_username,
            'add_agent': add_agent,
            'get_agent': get_agent,
            'update_agent': update_agent,
            'delete_agent': delete_agent,
        }

# Test the creation of a new agent with proper authorisation
def test_create_agent(db_manager_mocks):
    # Configure the mock for get_agent_by_username
    db_manager_mocks['get_agent_by_username'].return_value = None

    # Configure the mock for add_agent
    db_manager_mocks['add_agent'].return_value = Agents(
        id=uuid.uuid4(), ap_id="agent2", password_hash="hashed_pass", configuration={}, onboard=False
    )

    # Get a signed authorisation token with admin privileges
    auth_token = create_signed_jwt({"sub": "admin@example.com", "roles": "admin"})

    # Perform the request
    response = client.post(
        "/agents/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"ap_id": "agent2", "password": "testpassword", "configuration": {}}
    )

    # Verify the response
    assert response.status_code == 200
    assert response.json()["ap_id"] == "agent2"

# Test the retrieval of an agent
def test_get_agent(db_manager_mocks):
    # Configure the mock for get_agent
    db_manager_mocks['get_agent'].return_value = Agents(
        id=uuid.uuid4(), ap_id="agent1", password_hash="hashed_pass", configuration={}, onboard=True
    )

    # Get a signed authorisation token with admin privileges
    auth_token = create_signed_jwt({"sub": "admin@example.com", "roles": "admin"})

    # Perform the request
    response = client.get("/agents/agent1", headers={"Authorization": f"Bearer {auth_token}"})

    # Verify the response
    assert response.status_code == 200
    assert response.json()["ap_id"] == "agent1"

# Test updating an agent's configuration
def test_update_agent(db_manager_mocks):
    # Configure the mock for get_agent
    db_manager_mocks['get_agent'].return_value = Agents(
        id=uuid.uuid4(), ap_id="agent1", password_hash="hashed_pass", configuration={}, onboard=True
    )

    # Configure the mock for update_agent
    db_manager_mocks['update_agent'].return_value = Agents(
        id=uuid.uuid4(), ap_id="agent1", password_hash="hashed_pass", configuration={"key": "value"}, onboard=True
    )

    # Get a signed authorisation token with admin privileges
    auth_token = create_signed_jwt({"sub": "admin@example.com", "roles": "admin"})

    # Perform the request
    response = client.put(
        "/agents/agent1",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"configuration": {"key": "value"}}
    )

    # Verify the response
    assert response.status_code == 200
    assert response.json()["configuration"] == {"key": "value"}

# Test deleting an agent
def test_delete_agent(db_manager_mocks):
    # Configure the mock for delete_agent
    db_manager_mocks['delete_agent'].return_value = True

    # Get a signed authorisation token with admin privileges
    auth_token = create_signed_jwt({"sub": "admin@example.com", "roles": "admin"})

    # Perform the request
    response = client.delete("/agents/agent1", headers={"Authorization": f"Bearer {auth_token}"})

    # Verify the response
    assert response.status_code == 200
    assert response.json()["detail"] == "Agent agent1 deleted"