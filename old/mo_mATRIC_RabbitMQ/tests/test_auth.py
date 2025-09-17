# tests/test_auth.py

import pytest
from fastapi import HTTPException
from app.auth import auth_manager
from app.models import User, Agents, ThirdPartyApps
from app.database import DatabaseManager
from unittest.mock import Mock
from datetime import timedelta
from jose import jwt

# Define application's secret key and algorithm
SECRET_KEY = "f4e26a5290b9762bdbe668c50f9003d14ed9a5dda5c79a53cc188fcb8d64979e"  # Use the same secret key as application
ALGORITHM = "HS256"  # Ensure this matches the algorithm app_old uses

# Test password hashing and verification
def test_password_hashing():
    password = "securepassword"
    hashed_password = auth_manager.hash_password(password)

    assert auth_manager.verify_password(password, hashed_password) is True
    assert auth_manager.verify_password("wrongpassword", hashed_password) is False

# Test JWT token creation
def test_create_access_token():
    data = {"sub": "user1@example.com"}
    expires_delta = timedelta(minutes=15)
    token = auth_manager.create_access_token(data, expires_delta)

    # Decode token to verify contents
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_token["sub"] == "user1@example.com"
    assert "exp" in decoded_token  # Check that the expiration time is included

# Mock database manager for authentication tests
@pytest.fixture
def mock_db_manager():
    return Mock(spec=DatabaseManager)

# Test user authentication with correct credentials
def test_authenticate_user_success(mock_db_manager):
    mock_db_manager.get_user.return_value = User(
        id="1",
        username="user1@example.com",
        password_hash=auth_manager.hash_password("testpassword"),
        roles="user"
    )

    user = auth_manager.authenticate_user("user1@example.com", "testpassword", mock_db_manager)

    assert user is not None
    assert user.username == "user1@example.com"

# Test user authentication with incorrect credentials
def test_authenticate_user_failure(mock_db_manager):
    mock_db_manager.get_user.return_value = User(
        id="1",
        username="user1@example.com",
        password_hash=auth_manager.hash_password("testpassword"),
        roles="user"
    )

    user = auth_manager.authenticate_user("user1@example.com", "wrongpassword", mock_db_manager)

    assert user is None

# Test agent authentication with correct credentials
def test_authenticate_agent_success(mock_db_manager):
    mock_db_manager.get_agent_by_username.return_value = Agents(
        id="2",
        ap_id="agent1",
        password_hash=auth_manager.hash_password("testpassword"),
        configuration={},
        onboard=True
    )

    agent = auth_manager.authenticate_onboard_agent("agent1", "testpassword", mock_db_manager)

    assert agent is not None
    assert agent.ap_id == "agent1"

# Test agent authentication with onboarding
def test_authenticate_agent_onboarding(mock_db_manager):
    # Configure the agent to have onboarding as False initially
    agent = Agents(
        id="2",
        ap_id="agent1",
        password_hash=auth_manager.hash_password("testpassword"),
        configuration={},
        onboard=False
    )

    mock_db_manager.get_agent_by_username.return_value = agent

    # Mock the method that updates the onboard status
    mock_db_manager.update_agent_onboard_status = Mock()

    authenticated_agent = auth_manager.authenticate_onboard_agent("agent1", "testpassword", mock_db_manager)

    assert authenticated_agent is not None
    assert authenticated_agent.onboard is True

    # Verify that the onboard status update method was called
    mock_db_manager.update_agent_onboard_status.assert_called_once_with(authenticated_agent)

# Test agent authentication with incorrect credentials
def test_authenticate_agent_failure(mock_db_manager):
    mock_db_manager.get_agent_by_username.return_value = Agents(
        id="2",
        ap_id="agent1",
        password_hash=auth_manager.hash_password("testpassword"),
        configuration={},
        onboard=True
    )

    agent = auth_manager.authenticate_onboard_agent("agent1", "wrongpassword", mock_db_manager)

    assert agent is None

# Test third-party app_old authentication with correct credentials
def test_authenticate_third_party_app_success(mock_db_manager):
    mock_db_manager.get_third_party_app.return_value = ThirdPartyApps(
        id="3",
        app_name="app1",
        api_key="key1",
        permissions={"read": True, "write": False}
    )

    app = auth_manager.authenticate_third_party_app("app1", "key1", mock_db_manager)

    assert app is not None
    assert app.app_name == "app1"

# Test third-party app_old authentication with incorrect credentials
def test_authenticate_third_party_app_failure(mock_db_manager):
    mock_db_manager.get_third_party_app.return_value = ThirdPartyApps(
        id="3",
        app_name="app1",
        api_key="key1",
        permissions={"read": True, "write": False}
    )

    app = auth_manager.authenticate_third_party_app("app1", "wrongkey", mock_db_manager)

    assert app is None

# Test getting the current user with a valid token
def test_get_current_user_success(mock_db_manager):
    mock_db_manager.get_user.return_value = User(
        id="1",
        username="user1@example.com",
        password_hash=auth_manager.hash_password("testpassword"),
        roles="user"
    )

    # Create a token for the test user
    token = auth_manager.create_access_token({"sub": "user1@example.com"})

    user = auth_manager.get_current_user(token, mock_db_manager)

    assert user is not None
    assert user.username == "user1@example.com"

# Test getting the current user with an invalid token
def test_get_current_user_failure(mock_db_manager):
    # Create an invalid token
    token = "invalidtoken"

    with pytest.raises(HTTPException) as exc_info:
        auth_manager.get_current_user(token, mock_db_manager)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"
