import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app  # Adjust the import according to your project structure
from app.models import TokenData, UserCreate, UserUpdate

client = TestClient(app)

@pytest.fixture
def db_mock():
    with patch('app.database.DatabaseManager') as mock:
        yield mock

@pytest.fixture
def auth_manager_mock():
    with patch('app.auth.auth_manager') as mock:
        yield mock

@pytest.fixture
def current_user_mock():
    with patch('app.auth.get_current_user') as mock:
        yield mock

def test_create_first_user(db_mock, auth_manager_mock):
    user_data = {
        "username": "test_user",
        "password": "test_password",
        "roles": ["user"]
    }
    password_hash = "hashed_test_password"
    new_user = TokenData(username="test_user", roles=["user"])

    db_instance = db_mock.return_value
    db_instance.get_user.return_value = None
    db_instance.add_user.return_value = new_user

    auth_manager_instance = auth_manager_mock.return_value
    auth_manager_instance.hash_password.return_value = password_hash

    response = client.post("/public", json=user_data)
    assert response.status_code == 200
    assert response.json()["username"] == user_data["username"]

def test_create_user(db_mock, auth_manager_mock, current_user_mock):
    user_data = {
        "username": "test_user",
        "password": "test_password",
        "roles": ["user"]
    }
    password_hash = "hashed_test_password"
    new_user = TokenData(username="test_user", roles=["user"])

    db_instance = db_mock.return_value
    db_instance.get_user.return_value = None
    db_instance.add_user.return_value = new_user

    auth_manager_instance = auth_manager_mock.return_value
    auth_manager_instance.hash_password.return_value = password_hash

    current_user_instance = current_user_mock.return_value
    current_user_instance.roles = ['admin']

    response = client.post("/", json=user_data)
    assert response.status_code == 200
    assert response.json()["username"] == user_data["username"]

def test_update_user(db_mock, auth_manager_mock, current_user_mock):
    username = "test_user"
    user_update = {
        "password": "new_password",
        "roles": ["user", "admin"]
    }
    password_hash = "hashed_new_password"
    updated_user = TokenData(username="test_user", roles=["user", "admin"])

    db_instance = db_mock.return_value
    db_instance.update_user.return_value = updated_user

    auth_manager_instance = auth_manager_mock.return_value
    auth_manager_instance.hash_password.return_value = password_hash

    current_user_instance = current_user_mock.return_value
    current_user_instance.roles = ['admin']

    response = client.put(f"/{username}", json=user_update)
    assert response.status_code == 200
    assert response.json()["roles"] == user_update["roles"]

def test_delete_user(db_mock, current_user_mock):
    username = "test_user"

    db_instance = db_mock.return_value
    db_instance.delete_user.return_value = True

    current_user_instance = current_user_mock.return_value
    current_user_instance.roles = ['admin']

    response = client.delete(f"/{username}")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_get_user(db_mock):
    username = "test_user"
    user = TokenData(username="test_user", roles=["user"])

    db_instance = db_mock.return_value
    db_instance.get_user.return_value = user

    response = client.get(f"/{username}")
    assert response.status_code == 200
    assert response.json()["username"] == username

def test_list_users(db_mock):
    users = [
        TokenData(username="user1", roles=["user"]),
        TokenData(username="user2", roles=["admin"]),
    ]

    db_instance = db_mock.return_value
    db_instance.get_all_users.return_value = users

    response = client.get("/")
    assert response.status_code == 200
    assert len(response.json()) == len(users)

def test_read_users_me(current_user_mock):
    current_user = TokenData(username="test_user", roles=["user"])

    current_user_instance = current_user_mock.return_value
    current_user_instance.return_value = current_user

    response = client.get("/me")
    assert response.status_code == 200
    assert response.json()["username"] == current_user.username

if __name__ == '__main__':
    pytest.main()
