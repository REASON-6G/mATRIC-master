# tests/test_users.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import TokenData, UserCreate, UserUpdate
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
    with patch('app.database.DatabaseManager.get_user') as get_user, \
         patch('app.database.DatabaseManager.add_user') as add_user, \
         patch('app.database.DatabaseManager.update_user') as update_user, \
         patch('app.database.DatabaseManager.delete_user') as delete_user, \
         patch('app.database.DatabaseManager.get_all_users') as get_all_users:

        yield {
            'get_user': get_user,
            'add_user': add_user,
            'update_user': update_user,
            'delete_user': delete_user,
            'get_all_users': get_all_users,
        }

# Test the creation of a new user with proper authorisation
def test_create_user(db_manager_mocks):
    # Configure the mock for add_user
    db_manager_mocks['add_user'].return_value = {
        "id": str(uuid.uuid4()),  # Ensure the id is returned as expected
        "username": "user1@example.com",
        "roles": "user",  # Ensure roles are returned as a single string
    }

    # Configure the mock for get_user to return None (user doesn't exist yet)
    db_manager_mocks['get_user'].return_value = None

    # Get a signed authorisation token with admin privileges
    auth_token = create_signed_jwt({"sub": "admin@example.com", "roles": "admin"})

    # Perform the request
    response = client.post(
        "/users/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"username": "user1@example.com", "password": "testpassword", "roles": ["user"]}
    )

    # Verify the response
    assert response.status_code == 200
    assert response.json()["username"] == "user1@example.com"
    assert response.json()["roles"] == "user"

# Test the retrieval of a user
def test_get_user(db_manager_mocks):
    # Configure the mock for get_user
    db_manager_mocks['get_user'].return_value = TokenData(
        username="user1@example.com", roles="user", scopes=[]
    )

    # Get a signed authorisation token with admin privileges
    auth_token = create_signed_jwt({"sub": "admin@example.com", "roles": "admin"})

    # Perform the request
    response = client.get("/users/user1@example.com", headers={"Authorization": f"Bearer {auth_token}"})

    # Verify the response
    assert response.status_code == 200
    assert response.json()["username"] == "user1@example.com"
    assert response.json()["roles"] == "user"

# Test updating a user's information
def test_update_user(db_manager_mocks):
    # Configure the mock for update_user
    db_manager_mocks['update_user'].return_value = {
        "id": str(uuid.uuid4()),
        "username": "user1@example.com",
        "roles": "admin",  # Ensure roles are returned as a single string
    }

    # Get a signed authorisation token with admin privileges
    auth_token = create_signed_jwt({"sub": "admin@example.com", "roles": "admin"})

    # Perform the request
    response = client.put(
        "/users/user1@example.com",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"password": "newpassword", "roles": ["admin"]}
    )

    # Verify the response
    assert response.status_code == 200
    assert response.json()["roles"] == "admin"

# Test deleting a user
def test_delete_user(db_manager_mocks):
    # Configure the mock for delete_user
    db_manager_mocks['delete_user'].return_value = True

    # Get a signed authorisation token with admin privileges
    auth_token = create_signed_jwt({"sub": "admin@example.com", "roles": "admin"})

    # Perform the request
    response = client.delete("/users/user1@example.com", headers={"Authorization": f"Bearer {auth_token}"})

    # Verify the response
    assert response.status_code == 200
    assert response.json()["detail"] == "User user1@example.com deleted"

# Test listing all users
def test_list_users(db_manager_mocks):
    # Configure the mock for get_all_users
    db_manager_mocks['get_all_users'].return_value = [
        TokenData(username="user1@example.com", roles="user", scopes=[]),
        TokenData(username="user2@example.com", roles="admin", scopes=[]),
    ]

    # Get a signed authorisation token with admin privileges
    auth_token = create_signed_jwt({"sub": "admin@example.com", "roles": "admin"})

    # Perform the request
    response = client.get("/users/", headers={"Authorization": f"Bearer {auth_token}"})

    # Verify the response
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["username"] == "user1@example.com"
    assert response.json()[0]["roles"] == "user"
    assert response.json()[1]["username"] == "user2@example.com"
    assert response.json()[1]["roles"] == "admin"