import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app  # Adjust the import according to your project structure
from app.models import ThirdPartyApp, ThirdPartyAppCreate, ThirdPartyAppUpdate, TokenData

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

def test_create_third_party_app(db_mock, current_user_mock):
    app_data = {
        "app_name": "test_app",
        "api_key": "test_api_key",
        "permissions": {"key": "value"}
    }

    db_instance = db_mock.return_value
    db_instance.add_third_party_app.return_value = ThirdPartyApp(
        app_name=app_data["app_name"],
        api_key=app_data["api_key"],
        permissions=app_data["permissions"]
    )

    current_user_instance = current_user_mock.return_value
    current_user_instance.roles = ['admin']

    response = client.post("/", json=app_data)
    assert response.status_code == 200
    assert response.json()["app_name"] == app_data["app_name"]

def test_get_third_party_app(db_mock, current_user_mock):
    app_name = "test_app"
    third_party_app = ThirdPartyApp(
        app_name=app_name,
        api_key="test_api_key",
        permissions={"key": "value"}
    )

    db_instance = db_mock.return_value
    db_instance.get_third_party_app.return_value = third_party_app

    current_user_instance = current_user_mock.return_value
    current_user_instance.roles = ['admin']

    response = client.get(f"/{app_name}")
    assert response.status_code == 200
    assert response.json()["app_name"] == app_name

def test_update_third_party_app(db_mock, current_user_mock):
    app_name = "test_app"
    app_update = {
        "api_key": "new_api_key",
        "permissions": {"key": "new_value"}
    }
    updated_app = ThirdPartyApp(
        app_name=app_name,
        api_key=app_update["api_key"],
        permissions=app_update["permissions"]
    )

    db_instance = db_mock.return_value
    db_instance.update_third_party_app.return_value = updated_app

    current_user_instance = current_user_mock.return_value
    current_user_instance.roles = ['admin']

    response = client.put(f"/{app_name}", json=app_update)
    assert response.status_code == 200
    assert response.json()["api_key"] == app_update["api_key"]

def test_delete_third_party_app(db_mock, current_user_mock):
    app_name = "test_app"

    db_instance = db_mock.return_value
    db_instance.delete_third_party_app.return_value = True

    current_user_instance = current_user_mock.return_value
    current_user_instance.roles = ['admin']

    response = client.delete(f"/{app_name}")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["detail"] == f"Third-party app {app_name} deleted"

if __name__ == '__main__':
    pytest.main()
