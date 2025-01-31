# tests/test_database.py

import pytest
from unittest.mock import Mock, MagicMock
from app.database import DatabaseManager
from app.models import User, Agents, ThirdPartyApps
import uuid

# Mock SQLAlchemy session
@pytest.fixture
def mock_session():
    return MagicMock()

# Test user operations
def test_add_user(mock_session):
    db_manager = DatabaseManager(mock_session)

    # Define test data
    username = "user1@example.com"
    password_hash = "hashedpassword"
    roles = "user"

    # Mock user instance to return when added
    mock_user = User(id=uuid.uuid4(), username=username, password_hash=password_hash, roles=roles)

    # Set the return value for querying the added user
    mock_session.query.return_value.filter.return_value.first.return_value = None

    # Mock the add, commit, and refresh operations
    mock_session.add = Mock()
    mock_session.commit = Mock()
    mock_session.refresh = Mock()

    # Call the method
    result = db_manager.add_user(username, password_hash, roles)

    # Verify interactions and results
    mock_session.add.assert_called_once()  # Ensure something was added to the session
    mock_session.commit.assert_called_once()  # Ensure commit was called
    mock_session.refresh.assert_called_once_with(result)  # Ensure the added object was refreshed
    assert result.username == username
    assert result.roles == roles


def test_get_user(mock_session):
    db_manager = DatabaseManager(mock_session)

    # Define test data
    username = "user1@example.com"

    # Mock user instance
    mock_user = User(id=uuid.uuid4(), username=username, password_hash="hashedpassword", roles="user")
    mock_session.query.return_value.filter.return_value.first.return_value = mock_user

    # Call the method
    result = db_manager.get_user(username)

    # Verify the result
    assert result.username == username
    assert result.roles == "user"

def test_update_user(mock_session):
    db_manager = DatabaseManager(mock_session)

    # Define test data
    username = "user1@example.com"
    new_password_hash = "newhashedpassword"
    new_roles = "admin"

    # Mock existing user instance
    mock_user = User(id=uuid.uuid4(), username=username, password_hash="hashedpassword", roles="user")
    mock_session.query.return_value.filter.return_value.first.return_value = mock_user

    # Call the method
    result = db_manager.update_user(username, new_password_hash, new_roles)

    # Verify updates and interactions
    assert result.password_hash == new_password_hash
    assert result.roles == new_roles
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(mock_user)

def test_delete_user(mock_session):
    db_manager = DatabaseManager(mock_session)

    # Define test data
    username = "user1@example.com"

    # Mock existing user instance
    mock_user = User(id=uuid.uuid4(), username=username, password_hash="hashedpassword", roles="user")
    mock_session.query.return_value.filter.return_value.first.return_value = mock_user

    # Call the method
    result = db_manager.delete_user(username)

    # Verify deletion and interactions
    assert result is True
    mock_session.delete.assert_called_once_with(mock_user)
    mock_session.commit.assert_called_once()

def test_get_all_users(mock_session):
    db_manager = DatabaseManager(mock_session)

    # Mock user instances
    mock_user1 = User(id=uuid.uuid4(), username="user1@example.com", password_hash="hashedpassword1", roles="user")
    mock_user2 = User(id=uuid.uuid4(), username="user2@example.com", password_hash="hashedpassword2", roles="admin")
    mock_session.query.return_value.all.return_value = [mock_user1, mock_user2]

    # Call the method
    result = db_manager.get_all_users()

    # Verify the result
    assert len(result) == 2
    assert result[0].username == "user1@example.com"
    assert result[1].username == "user2@example.com"

# Test agent operations
def test_add_agent(mock_session):
    db_manager = DatabaseManager(mock_session)

    # Define test data
    ap_id = "agent1"
    password_hash = "hashedpassword"
    configuration = {}

    # Mock agent instance to return when added
    mock_agent = Agents(id=uuid.uuid4(), ap_id=ap_id, password_hash=password_hash, configuration=configuration, onboard=False)

    # Set the return value for querying the added agent
    mock_session.query.return_value.filter.return_value.first.return_value = None

    # Mock the add, commit, and refresh operations
    mock_session.add = Mock()
    mock_session.commit = Mock()
    mock_session.refresh = Mock()

    # Call the method
    result = db_manager.add_agent(ap_id, password_hash, configuration)

    # Verify interactions and results
    mock_session.add.assert_called_once()  # Ensure something was added to the session
    mock_session.commit.assert_called_once()  # Ensure commit was called
    mock_session.refresh.assert_called_once_with(result)  # Ensure the added object was refreshed
    assert result.ap_id == ap_id
    assert result.configuration == configuration


def test_get_agent(mock_session):
    db_manager = DatabaseManager(mock_session)

    # Define test data
    ap_id = "agent1"

    # Mock agent instance
    mock_agent = Agents(id=uuid.uuid4(), ap_id=ap_id, password_hash="hashedpassword", configuration={}, onboard=True)
    mock_session.query.return_value.filter.return_value.first.return_value = mock_agent

    # Call the method
    result = db_manager.get_agent(ap_id)

    # Verify the result
    assert result.ap_id == ap_id
    assert result.onboard is True

def test_update_agent(mock_session):
    db_manager = DatabaseManager(mock_session)

    # Define test data
    ap_id = "agent1"
    new_configuration = {"key": "value"}
    new_supported_commands = ["command1", "command2"]

    # Mock existing agent instance
    mock_agent = Agents(id=uuid.uuid4(), ap_id=ap_id, password_hash="hashedpassword", configuration={}, onboard=True)
    mock_session.query.return_value.filter.return_value.first.return_value = mock_agent

    # Call the method
    result = db_manager.update_agent(ap_id, new_configuration, new_supported_commands)

    # Verify updates and interactions
    assert result.configuration == new_configuration
    assert result.supported_commands == new_supported_commands
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(mock_agent)

def test_delete_agent(mock_session):
    db_manager = DatabaseManager(mock_session)

    # Define test data
    ap_id = "agent1"

    # Mock existing agent instance
    mock_agent = Agents(id=uuid.uuid4(), ap_id=ap_id, password_hash="hashedpassword", configuration={}, onboard=True)
    mock_session.query.return_value.filter.return_value.first.return_value = mock_agent

    # Call the method
    result = db_manager.delete_agent(ap_id)

    # Verify deletion and interactions
    assert result is True
    mock_session.delete.assert_called_once_with(mock_agent)
    mock_session.commit.assert_called_once()

def test_get_all_agents(mock_session):
    db_manager = DatabaseManager(mock_session)

    # Mock agent instances
    mock_agent1 = Agents(id=uuid.uuid4(), ap_id="agent1", password_hash="hashedpassword1", configuration={}, onboard=True)
    mock_agent2 = Agents(id=uuid.uuid4(), ap_id="agent2", password_hash="hashedpassword2", configuration={}, onboard=False)
    mock_session.query.return_value.all.return_value = [mock_agent1, mock_agent2]

    # Call the method
    result = db_manager.get_all_agents()

    # Verify the result
    assert len(result) == 2
    assert result[0].ap_id == "agent1"
    assert result[1].ap_id == "agent2"

# Test third-party app_old operations
def test_add_third_party_app(mock_session):
    db_manager = DatabaseManager(mock_session)

    # Define test data
    app_name = "app1"
    api_key = "apikey"
    permissions = {"read": True, "write": False}

    # Mock third-party app_old instance to return when added
    mock_app = ThirdPartyApps(id=uuid.uuid4(), app_name=app_name, api_key=api_key, permissions=permissions)

    # Set the return value for querying the added app_old
    mock_session.query.return_value.filter.return_value.first.return_value = None

    # Mock the add, commit, and refresh operations
    mock_session.add = Mock()
    mock_session.commit = Mock()
    mock_session.refresh = Mock()

    # Call the method
    result = db_manager.add_third_party_app(app_name, api_key, permissions)

    # Verify interactions and results
    mock_session.add.assert_called_once()  # Ensure something was added to the session
    mock_session.commit.assert_called_once()  # Ensure commit was called
    mock_session.refresh.assert_called_once_with(result)  # Ensure the added object was refreshed
    assert result.app_name == app_name
    assert result.permissions == permissions


def test_get_third_party_app(mock_session):
    db_manager = DatabaseManager(mock_session)

    # Define test data
    app_name = "app1"

    # Mock third-party app_old instance
    mock_app = ThirdPartyApps(id=uuid.uuid4(), app_name=app_name, api_key="apikey", permissions={"read": True, "write": False})
    mock_session.query.return_value.filter.return_value.first.return_value = mock_app

    # Call the method
    result = db_manager.get_third_party_app(app_name)

    # Verify the result
    assert result.app_name == app_name
    assert result.permissions == {"read": True, "write": False}

def test_update_third_party_app(mock_session):
    db_manager = DatabaseManager(mock_session)

    # Define test data
    app_name = "app1"
    new_api_key = "newapikey"
    new_permissions = {"read": False, "write": True}

    # Mock existing third-party app_old instance
    mock_app = ThirdPartyApps(id=uuid.uuid4(), app_name=app_name, api_key="apikey", permissions={"read": True, "write": False})
    mock_session.query.return_value.filter.return_value.first.return_value = mock_app

    # Call the method
    result = db_manager.update_third_party_app(app_name, new_api_key, new_permissions)

    # Verify updates and interactions
    assert result.api_key == new_api_key
    assert result.permissions == new_permissions
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(mock_app)

def test_delete_third_party_app(mock_session):
    db_manager = DatabaseManager(mock_session)

    # Define test data
    app_name = "app1"

    # Mock existing third-party app_old instance
    mock_app = ThirdPartyApps(id=uuid.uuid4(), app_name=app_name, api_key="apikey", permissions={"read": True, "write": False})
    mock_session.query.return_value.filter.return_value.first.return_value = mock_app

    # Call the method
    result = db_manager.delete_third_party_app(app_name)

    # Verify deletion and interactions
    assert result is True
    mock_session.delete.assert_called_once_with(mock_app)
    mock_session.commit.assert_called_once()

def test_get_all_third_party_apps(mock_session):
    db_manager = DatabaseManager(mock_session)

    # Mock third-party app_old instances
    mock_app1 = ThirdPartyApps(id=uuid.uuid4(), app_name="app1", api_key="apikey1", permissions={"read": True, "write": False})
    mock_app2 = ThirdPartyApps(id=uuid.uuid4(), app_name="app2", api_key="apikey2", permissions={"read": False, "write": True})
    mock_session.query.return_value.all.return_value = [mock_app1, mock_app2]

    # Call the method
    result = db_manager.get_all_third_party_apps()

    # Verify the result
    assert len(result) == 2
    assert result[0].app_name == "app1"
    assert result[1].app_name == "app2"
