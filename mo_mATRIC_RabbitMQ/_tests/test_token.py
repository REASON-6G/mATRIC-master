import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app  # Adjust the import according to your project structure
from app.models import Token

client = TestClient(app)

@pytest.fixture
def db_mock():
    with patch('app_old.database.DatabaseManager') as mock:
        yield mock

@pytest.fixture
def auth_manager_mock():
    with patch('app_old.auth.auth_manager') as mock:
        yield mock

@pytest.fixture
def settings_mock():
    with patch('app_old.config.settings') as mock:
        yield mock

def test_login_user_success(db_mock, auth_manager_mock, settings_mock):
    settings_mock.access_token_expire_minutes = 30
    form_data = {
        "username": "test_user",
        "password": "test_password"
    }
    token_data = {
        "access_token": "mock_token",
        "token_type": "bearer",
        "expires_in": 1800  # 30 minutes in seconds
    }

    db_instance = db_mock.return_value
    auth_manager_instance = auth_manager_mock.return_value
    auth_manager_instance.authenticate_user.return_value = MagicMock(username="test_user")
    auth_manager_instance.create_access_token.return_value = token_data["access_token"]

    response = client.post("/", data=form_data, params={"login_type": "user"})
    assert response.status_code == 200
    assert response.json()["access_token"] == token_data["access_token"]

def test_login_agent_success(db_mock, auth_manager_mock, settings_mock):
    settings_mock.access_token_expire_minutes = 30
    form_data = {
        "username": "test_agent",
        "password": "test_password"
    }
    token_data = {
        "access_token": "mock_token",
        "token_type": "bearer",
        "expires_in": 1800  # 30 minutes in seconds
    }

    db_instance = db_mock.return_value
    auth_manager_instance = auth_manager_mock.return_value
    auth_manager_instance.authenticate_onboard_agent.return_value = MagicMock(ap_id="test_agent")
    auth_manager_instance.create_access_token.return_value = token_data["access_token"]

    response = client.post("/", data=form_data, params={"login_type": "agent"})
    assert response.status_code == 200
    assert response.json()["access_token"] == token_data["access_token"]

def test_login_third_party_app_success(db_mock, auth_manager_mock, settings_mock):
    settings_mock.access_token_expire_minutes = 30
    form_data = {
        "username": "test_app",
        "password": "test_api_key"
    }
    token_data = {
        "access_token": "mock_token",
        "token_type": "bearer",
        "expires_in": 1800  # 30 minutes in seconds
    }

    db_instance = db_mock.return_value
    auth_manager_instance = auth_manager_mock.return_value
    auth_manager_instance.authenticate_third_party_app.return_value = MagicMock(app_name="test_app")
    auth_manager_instance.create_access_token.return_value = token_data["access_token"]

    response = client.post("/", data=form_data, params={"login_type": "third_party_app"})
    assert response.status_code == 200
    assert response.json()["access_token"] == token_data["access_token"]

def test_login_invalid_login_type():
    form_data = {
        "username": "test_user",
        "password": "test_password"
    }

    response = client.post("/", data=form_data, params={"login_type": "invalid_type"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid login type"

def test_login_missing_login_type():
    form_data = {
        "username": "test_user",
        "password": "test_password"
    }

    response = client.post("/", data=form_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Login type is required"

def test_login_incorrect_credentials(db_mock, auth_manager_mock):
    form_data = {
        "username": "test_user",
        "password": "wrong_password"
    }

    auth_manager_instance = auth_manager_mock.return_value
    auth_manager_instance.authenticate_user.return_value = None

    response = client.post("/", data=form_data, params={"login_type": "user"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

if __name__ == '__main__':
    pytest.main()
