import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from app.database import DatabaseManager
from app.models import User, Agent, ThirdPartyApp, UserCreate, UserUpdate

@pytest.fixture
def db_session():
    with patch('sqlalchemy.orm.Session') as mock:
        yield mock

@pytest.fixture
def db_manager(db_session):
    return DatabaseManager(db=db_session)

def test_get_user(db_manager):
    user = User(username="test_user", password_hash="hashed_password", roles="user")
    db_manager.db.query(User).filter(User.username == "test_user").first.return_value = user
    
    result = db_manager.get_user("test_user")
    assert result == user

def test_add_user(db_manager):
    user_data = UserCreate(username="test_user", password="test_password", roles=["user"])
    new_user = User(username=user_data.username, password_hash="hashed_password", roles="user")
    
    db_manager.db.add.return_value = None
    db_manager.db.commit.return_value = None
    db_manager.db.refresh.return_value = new_user
    
    result = db_manager.add_user(user_data.username, "hashed_password", user_data.roles)
    assert result == new_user

def test_update_user(db_manager):
    user_data = UserUpdate(password="new_password", roles=["admin"])
    user = User(username="test_user", password_hash="hashed_password", roles="user")
    
    db_manager.db.query(User).filter(User.username == "test_user").first.return_value = user
    
    updated_user = User(username="test_user", password_hash="new_hashed_password", roles="admin")
    db_manager.db.commit.return_value = None
    db_manager.db.refresh.return_value = updated_user
    
    result = db_manager.update_user("test_user", "new_hashed_password", user_data.roles)
    assert result == updated_user

def test_delete_user(db_manager):
    user = User(username="test_user", password_hash="hashed_password", roles="user")
    
    db_manager.db.query(User).filter(User.username == "test_user").first.return_value = user
    db_manager.db.delete.return_value = None
    db_manager.db.commit.return_value = None
    
    result = db_manager.delete_user("test_user")
    assert result is True

def test_get_agent(db_manager):
    agent = Agent(ap_id="test_ap_id", username="test_agent", password_hash="hashed_password", configuration={}, supported_commands=[])
    db_manager.db.query(Agent).filter(Agent.ap_id == "test_ap_id").first.return_value = agent
    
    result = db_manager.get_agent("test_ap_id")
    assert result == agent

def test_add_agent(db_manager):
    new_agent = Agent(ap_id="test_ap_id", username="test_agent", password_hash="hashed_password", configuration={}, supported_commands=[])
    
    db_manager.db.add.return_value = None
    db_manager.db.commit.return_value = None
    db_manager.db.refresh.return_value = new_agent
    
    result = db_manager.add_agent("test_ap_id", "test_agent", "hashed_password", [], {}, [])
    assert result == new_agent

def test_update_agent(db_manager):
    agent = Agent(ap_id="test_ap_id", username="test_agent", password_hash="hashed_password", configuration={}, supported_commands=[])
    
    db_manager.db.query(Agent).filter(Agent.ap_id == "test_ap_id").first.return_value = agent
    
    updated_agent = Agent(ap_id="test_ap_id", username="test_agent", password_hash="hashed_password", configuration={"key": "value"}, supported_commands=["command"])
    db_manager.db.commit.return_value = None
    db_manager.db.refresh.return_value = updated_agent
    
    result = db_manager.update_agent("test_ap_id", {"key": "value"}, ["command"])
    assert result == updated_agent

def test_delete_agent(db_manager):
    agent = Agent(ap_id="test_ap_id", username="test_agent", password_hash="hashed_password", configuration={}, supported_commands=[])
    
    db_manager.db.query(Agent).filter(Agent.ap_id == "test_ap_id").first.return_value = agent
    db_manager.db.delete.return_value = None
    db_manager.db.commit.return_value = None
    
    result = db_manager.delete_agent("test_ap_id")
    assert result is True

def test_get_third_party_app(db_manager):
    app = ThirdPartyApp(app_name="test_app", api_key="test_api_key", permissions={})
    db_manager.db.query(ThirdPartyApp).filter(ThirdPartyApp.app_name == "test_app").first.return_value = app
    
    result = db_manager.get_third_party_app("test_app")
    assert result == app

def test_add_third_party_app(db_manager):
    new_app = ThirdPartyApp(app_name="test_app", api_key="test_api_key", permissions={})
    
    db_manager.db.add.return_value = None
    db_manager.db.commit.return_value = None
    db_manager.db.refresh.return_value = new_app
    
    result = db_manager.add_third_party_app("test_app", "test_api_key", {})
    assert result == new_app

def test_update_third_party_app(db_manager):
    app = ThirdPartyApp(app_name="test_app", api_key="test_api_key", permissions={})
    
    db_manager.db.query(ThirdPartyApp).filter(ThirdPartyApp.app_name == "test_app").first.return_value = app
    
    updated_app = ThirdPartyApp(app_name="test_app", api_key="new_test_api_key", permissions={"key": "value"})
    db_manager.db.commit.return_value = None
    db_manager.db.refresh.return_value = updated_app
    
    result = db_manager.update_third_party_app("test_app", "new_test_api_key", {"key": "value"})
    assert result == updated_app

def test_delete_third_party_app(db_manager):
    app = ThirdPartyApp(app_name="test_app", api_key="test_api_key", permissions={})
    
    db_manager.db.query(ThirdPartyApp).filter(ThirdPartyApp.app_name == "test_app").first.return_value = app
    db_manager.db.delete.return_value = None
    db_manager.db.commit.return_value = None
    
    result = db_manager.delete_third_party_app("test_app")
    assert result is True

if __name__ == "__main__":
    pytest.main()
