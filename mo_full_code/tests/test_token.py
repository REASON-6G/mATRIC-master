# tests/test_token.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth import auth_manager
from app.models import User, Agents, ThirdPartyApps
from unittest.mock import patch

# Create a TestClient instance
client = TestClient(app)

# Define application's secret key and algorithm
SECRET_KEY = "f4e26a5290b9762bdbe668c50f9003d14ed9a5dda5c79a53cc188fcb8d64979e"  # Use the same secret key as application
ALGORITHM = "HS256"  # Ensure this matches the algorithm app uses

@pytest.fixture
def db_manager_mocks():
    """Provide mock implementations of database manager methods."""
    with patch('app.database.DatabaseManager.get_user') as get_user, \
         patch('app.database.DatabaseManager.get_agent_by_username') as get_agent_by_username, \
         patch('app.database.DatabaseManager.get_third_party_app') as get_third_party_app:

        yield {
            'get_user': get_user,
            'get_agent_by_username': get_agent_by_username,
            'get_third_party_app': get_third_party_app,
        }

# Test user login with correct credentials
def test_user_login_success(db_manager_mocks):
    # Configure the mock for get_user
    db_manager_mocks['get_user'].return_value = User(
        id="1",
        username="user1@example.com",
        password_hash=auth_manager.hash_password("testpassword"),
        roles="user"
    )

    # Perform the login request
    response = client.post(
        "/token/?login_type=user",
        data={"username": "user1@example.com", "password": "testpassword", "grant_type": "password"}
    )

    # Verify the response
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

# Test user login with incorrect credentials
def test_user_login_failure(db_manager_mocks):
    # Configure the mock for get_user to return None (user not found)
    db_manager_mocks['get_user'].return_value = None

    # Perform the login request with incorrect credentials
    response = client.post(
        "/token/?login_type=user",
        data={"username": "user1@example.com", "password": "wrongpassword", "grant_type": "password"}
    )

    # Verify the response
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

# Test agent login with correct credentials
def test_agent_login_success(db_manager_mocks):
    # Configure the mock for get_agent_by_username
    db_manager_mocks['get_agent_by_username'].return_value = Agents(
        id="2",
        ap_id="agent1",
        password_hash=auth_manager.hash_password("testpassword"),
        configuration={},
        onboard=True
    )

    # Perform the login request for agent
    response = client.post(
        "/token/?login_type=agent",
        data={"username": "agent1", "password": "testpassword", "grant_type": "password"}
    )

    # Verify the response
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

# Test agent login with incorrect credentials
def test_agent_login_failure(db_manager_mocks):
    # Configure the mock for get_agent_by_username to return None (agent not found)
    db_manager_mocks['get_agent_by_username'].return_value = None

    # Perform the login request with incorrect credentials
    response = client.post(
        "/token/?login_type=agent",
        data={"username": "agent1", "password": "wrongpassword", "grant_type": "password"}
    )

    # Verify the response
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect agent credentials"

# Test third-party app login with correct credentials
def test_third_party_app_login_success(db_manager_mocks):
    # Configure the mock for get_third_party_app
    db_manager_mocks['get_third_party_app'].return_value = ThirdPartyApps(
        id="3",
        app_name="app1",
        api_key="key1",
        permissions={"read": True, "write": False}
    )

    # Perform the login request for third-party app
    response = client.post(
        "/token/?login_type=third_party_app",
        data={"username": "app1", "password": "key1", "grant_type": "password"}
    )

    # Verify the response
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

# Test third-party app login with incorrect credentials
def test_third_party_app_login_failure(db_manager_mocks):
    # Configure the mock for get_third_party_app to return None (app not found)
    db_manager_mocks['get_third_party_app'].return_value = None

    # Perform the login request with incorrect credentials
    response = client.post(
        "/token/?login_type=third_party_app",
        data={"username": "app1", "password": "wrongkey", "grant_type": "password"}
    )

    # Verify the response
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect API ID or API key"
