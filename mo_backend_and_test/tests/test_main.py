# tests/test_main.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.auth import auth_manager


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_token():
    # Create a mock token with admin role
    token_data = {"sub": "adminuser", "roles": "admin"}
    return auth_manager.create_access_token(data=token_data)


@pytest.fixture
def third_party_app_token():
    # Create a mock token for a third-party app with necessary permissions
    token_data = {"sub": "thirdpartyapp", "roles": "third_party_app", "permissions": {"read": True}}
    return auth_manager.create_access_token(data=token_data)


@pytest.fixture
def mock_db():
    # Mock the database session
    with patch('app.dependencies.get_db', autospec=True) as mock_get_db:
        db = MagicMock()
        mock_get_db.return_value = db
        yield db


def test_token_endpoint_user(client):
    response = client.post(
        "/token/?login_type=user",
        data={
            "username": "testuser",
            "password": "testpass"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code in {200, 401}


def test_token_endpoint_agent(client):
    response = client.post(
        "/token/?login_type=agent",
        data={
            "username": "testagent",
            "password": "agentpass"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code in {200, 401}


def test_token_endpoint_third_party_app(client):
    response = client.post(
        "/token/?login_type=third_party_app",
        data={
            "username": "testapp",
            "password": "apppass"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code in {200, 401}


def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 404


def test_users_endpoint(client):
    response = client.get("/users/nonexistentuser")
    assert response.status_code == 404


def test_agents_endpoint_unauthorized(client, mock_db):
    # Test unauthorized access without a token
    response = client.get("/agents/agent1")
    assert response.status_code == 401


def test_third_party_apps_endpoint_unauthorized(client, mock_db):
    # Test unauthorized access without a token
    response = client.get("/third_party_apps/existentapp")
    assert response.status_code == 401


def test_cors_configuration_no_origins(client):
    # Test that no CORS headers are present when no origins are allowed
    response = client.options("/users/", headers={"Origin": "http://example.com"})
    assert response.headers.get("access-control-allow-origin") is None
    assert "access-control-allow-methods" not in response.headers