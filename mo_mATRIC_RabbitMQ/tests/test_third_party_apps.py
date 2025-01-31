# tests/test_third_party_apps.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import ThirdPartyApps, TokenData
from app.auth import get_current_user
from jose import jwt
from unittest.mock import patch
import uuid

# Create a TestClient instance
client = TestClient(app)

# Define application's secret key and algorithm
SECRET_KEY = "f4e26a5290b9762bdbe668c50f9003d14ed9a5dda5c79a53cc188fcb8d64979e"  # Use the same secret key as application
ALGORITHM = "HS256"  # Ensure this matches the algorithm app_old uses

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
    with patch('app_old.database.DatabaseManager.get_third_party_app') as get_third_party_app, \
         patch('app_old.database.DatabaseManager.add_third_party_app') as add_third_party_app, \
         patch('app_old.database.DatabaseManager.update_third_party_app') as update_third_party_app, \
         patch('app_old.database.DatabaseManager.delete_third_party_app') as delete_third_party_app:

        yield {
            'get_third_party_app': get_third_party_app,
            'add_third_party_app': add_third_party_app,
            'update_third_party_app': update_third_party_app,
            'delete_third_party_app': delete_third_party_app,
        }

# Test the creation of a new third-party app_old with proper authorization
def test_create_third_party_app(db_manager_mocks):
    # Configure the mock for add_third_party_app
    db_manager_mocks['add_third_party_app'].return_value = ThirdPartyApps(
        id=uuid.uuid4(), app_name="app1", api_key="key1", permissions={"read": True, "write": False}
    )

    # Get a signed authorisation token with admin privileges
    auth_token = create_signed_jwt({"sub": "admin@example.com", "roles": "admin"})

    # Perform the request
    response = client.post(
        "/third_party_apps/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"app_name": "app1", "api_key": "key1", "permissions": {"read": True, "write": False}}
    )

    # Verify the response
    assert response.status_code == 200
    assert response.json()["app_name"] == "app1"

# Test the retrieval of a third-party app_old
def test_get_third_party_app(db_manager_mocks):
    # Configure the mock for get_third_party_app
    db_manager_mocks['get_third_party_app'].return_value = ThirdPartyApps(
        id=uuid.uuid4(), app_name="app1", api_key="key1", permissions={"read": True, "write": False}
    )

    # Get a signed authorisation token with admin privileges
    auth_token = create_signed_jwt({"sub": "admin@example.com", "roles": "admin"})

    # Perform the request
    response = client.get("/third_party_apps/app1", headers={"Authorization": f"Bearer {auth_token}"})

    # Verify the response
    assert response.status_code == 200
    assert response.json()["app_name"] == "app1"

# Test updating a third-party app_old's configuration
def test_update_third_party_app(db_manager_mocks):
    # Configure the mock for update_third_party_app
    db_manager_mocks['update_third_party_app'].return_value = ThirdPartyApps(
        id=uuid.uuid4(), app_name="app1", api_key="new_key", permissions={"read": True, "write": True}
    )

    # Get a signed authorisation token with admin privileges
    auth_token = create_signed_jwt({"sub": "admin@example.com", "roles": "admin"})

    # Perform the request
    response = client.put(
        "/third_party_apps/app1",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"api_key": "new_key", "permissions": {"read": True, "write": True}}
    )

    # Verify the response
    assert response.status_code == 200
    assert response.json()["api_key"] == "new_key"
    assert response.json()["permissions"]["write"] is True

# Test deleting a third-party app_old
def test_delete_third_party_app(db_manager_mocks):
    # Configure the mock for delete_third_party_app
    db_manager_mocks['delete_third_party_app'].return_value = True

    # Get a signed authorisation token with admin privileges
    auth_token = create_signed_jwt({"sub": "admin@example.com", "roles": "admin"})

    # Perform the request
    response = client.delete("/third_party_apps/app1", headers={"Authorization": f"Bearer {auth_token}"})

    # Verify the response
    assert response.status_code == 200
    assert response.json()["detail"] == "Third-party app_old app1 deleted"
