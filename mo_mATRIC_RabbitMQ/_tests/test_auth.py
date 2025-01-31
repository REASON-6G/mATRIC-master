import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from jose import JWTError, jwt
from app.auth import AuthManager, get_current_user, oauth2_scheme
from app.config import settings
from app.database import DatabaseManager, get_db_manager
from app.models import TokenData

# Initialize AuthManager for testing
auth_manager = AuthManager()

@pytest.fixture
def db_mock():
    with patch('app_old.database.DatabaseManager') as mock:
        yield mock

@pytest.fixture
def settings_mock():
    with patch('app_old.config.settings') as mock:
        yield mock

def test_verify_password():
    plain_password = "test_password"
    hashed_password = auth_manager.hash_password(plain_password)
    assert auth_manager.verify_password(plain_password, hashed_password)

def test_create_access_token():
    data = {"sub": "test_user"}
    token = auth_manager.create_access_token(data)
    assert token is not None

def test_create_access_token_missing_sub():
    data = {"not_sub": "test_user"}
    with pytest.raises(ValueError, match="Token data should include sub field"):
        auth_manager.create_access_token(data)

def test_authenticate_user_success(db_mock):
    db_instance = db_mock.return_value
    user = MagicMock(password_hash=auth_manager.hash_password("test_password"))
    db_instance.get_user.return_value = user

    authenticated_user = auth_manager.authenticate_user("test_user", "test_password", db_instance)
    assert authenticated_user is not None

def test_authenticate_user_failure(db_mock):
    db_instance = db_mock.return_value
    db_instance.get_user.return_value = None

    authenticated_user = auth_manager.authenticate_user("test_user", "wrong_password", db_instance)
    assert authenticated_user is None

def test_get_current_user_success(db_mock, settings_mock):
    db_instance = db_mock.return_value
    settings_mock.jwt_secret_key = "secret"
    settings_mock.jwt_algorithm = "HS256"

    token_data = {"sub": "test_user"}
    token = jwt.encode(token_data, settings_mock.jwt_secret_key, algorithm=settings_mock.jwt_algorithm)

    user = MagicMock(username="test_user")
    db_instance.get_user.return_value = user

    current_user = auth_manager.get_current_user(token, db_instance)
    assert current_user.username == "test_user"

def test_get_current_user_failure_invalid_token(db_mock, settings_mock):
    db_instance = db_mock.return_value
    settings_mock.jwt_secret_key = "secret"
    settings_mock.jwt_algorithm = "HS256"

    invalid_token = "invalid_token"

    with pytest.raises(HTTPException) as excinfo:
        auth_manager.get_current_user(invalid_token, db_instance)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user_failure_user_not_found(db_mock, settings_mock):
    db_instance = db_mock.return_value
    settings_mock.jwt_secret_key = "secret"
    settings_mock.jwt_algorithm = "HS256"

    token_data = {"sub": "nonexistent_user"}
    token = jwt.encode(token_data, settings_mock.jwt_secret_key, algorithm=settings_mock.jwt_algorithm)

    db_instance.get_user.return_value = None

    with pytest.raises(HTTPException) as excinfo:
        auth_manager.get_current_user(token, db_instance)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.fixture
def token():
    data = {"sub": "test_user"}
    token = auth_manager.create_access_token(data)
    return token

def test_get_current_user_dependency(db_mock, token):
    db_instance = db_mock.return_value
    user = MagicMock(username="test_user")
    db_instance.get_user.return_value = user

    with patch('app_old.auth.oauth2_scheme', return_value=token):
        current_user = get_current_user(token=token, db=db_instance)
        assert current_user.username == "test_user"
