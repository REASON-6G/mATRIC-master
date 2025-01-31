# tests/test_database_operations.py

import pytest
from unittest.mock import MagicMock, create_autospec
from sqlalchemy.orm import Session
from app.models import User, Agents, ThirdPartyApps
from app.database import DatabaseManager

@pytest.fixture
def mock_session(mocker):
    return mocker.create_autospec(Session, instance=True)

@pytest.fixture
def db_manager(mock_session):
    return DatabaseManager(mock_session)

def test_create_user(db_manager, mock_session):
    # Setup: User does not exist initially
    mock_session.query().filter().first.return_value = None

    # Create user
    new_user = User(username="testuser", password_hash="hashed_pass", roles="admin")

    # Mock adding user
    db_manager.add_user = MagicMock(return_value=new_user)

    # Call the method under test
    result_user = db_manager.add_user(username="testuser", password_hash="hashed_pass", roles="admin")

    # Verify the result
    db_manager.add_user.assert_called_once_with(username="testuser", password_hash="hashed_pass", roles="admin")
    assert result_user.username == "testuser"
    assert result_user.roles == "admin"

def test_create_agent(db_manager, mock_session):
    # Setup: Agent does not exist initially
    mock_session.query().filter().first.return_value = None

    # Create agent
    new_agent = Agents(ap_id="agent123", password_hash="hashed_pass", configuration={}, onboard=False)

    # Mock adding agent
    db_manager.add_agent = MagicMock(return_value=new_agent)

    # Call the method under test
    result_agent = db_manager.add_agent(ap_id="agent123", password_hash="hashed_pass", configuration={})

    # Verify the result
    db_manager.add_agent.assert_called_once_with(ap_id="agent123", password_hash="hashed_pass", configuration={})
    assert result_agent.ap_id == "agent123"
    assert result_agent.onboard is False

def test_create_third_party_app(db_manager, mock_session):
    # Setup: App does not exist initially
    mock_session.query().filter().first.return_value = None

    # Create third-party app_old
    new_app = ThirdPartyApps(app_name="appXYZ", api_key="api_key_123", permissions={})

    # Mock adding third-party app_old
    db_manager.add_third_party_app = MagicMock(return_value=new_app)

    # Call the method under test
    result_app = db_manager.add_third_party_app(app_name="appXYZ", api_key="api_key_123", permissions={})

    # Verify the result
    db_manager.add_third_party_app.assert_called_once_with(app_name="appXYZ", api_key="api_key_123", permissions={})
    assert result_app.app_name == "appXYZ"