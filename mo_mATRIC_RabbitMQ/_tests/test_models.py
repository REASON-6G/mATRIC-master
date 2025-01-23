import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, Agents, ThirdPartyApps
from pydantic import ValidationError
from app.models import UserCreate, UserUpdate, AgentCreate, AgentUpdate, ThirdPartyAppCreate, ThirdPartyAppUpdate

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_user(db):
    user = User(
        username="test_user@example.com",
        password_hash="hashed_password",
        roles="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    assert user.id is not None
    assert user.username == "test_user@example.com"
    assert user.password_hash == "hashed_password"
    assert user.roles == "user"

def test_create_agent(db):
    agent = Agents(
        ap_id="test_agent",
        password_hash="hashed_password",
        configuration={"key": "value"},
        onboard=False
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    assert agent.id is not None
    assert agent.ap_id == "test_agent"
    assert agent.password_hash == "hashed_password"
    assert agent.configuration == {"key": "value"}
    assert agent.onboard is False

def test_create_third_party_app(db):
    app = ThirdPartyApps(
        app_name="test_app",
        api_key="test_api_key",
        permissions={"key": "value"}
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    assert app.id is not None
    assert app.app_name == "test_app"
    assert app.api_key == "test_api_key"
    assert app.permissions == {"key": "value"}

def test_user_create_pydantic():
    user = UserCreate(
        username="test_user@example.com",
        password="test_password",
        roles=["user"]
    )
    assert user.username == "test_user@example.com"
    assert user.password == "test_password"
    assert user.roles == ["user"]

def test_user_create_pydantic_invalid():
    with pytest.raises(ValidationError):
        UserCreate(
            username="invalid-email",
            password="test_password",
            roles=["user"]
        )

def test_agent_create_pydantic():
    agent = AgentCreate(
        ap_id="test_agent",
        password="test_password",
        configuration={"key": "value"}
    )
    assert agent.ap_id == "test_agent"
    assert agent.password == "test_password"
    assert agent.configuration == {"key": "value"}

def test_third_party_app_create_pydantic():
    app = ThirdPartyAppCreate(
        app_name="test_app",
        api_key="test_api_key",
        permissions={"key": "value"}
    )
    assert app.app_name == "test_app"
    assert app.api_key == "test_api_key"
    assert app.permissions == {"key": "value"}

def test_user_update_pydantic():
    user_update = UserUpdate(
        password="new_password",
        roles=["admin"]
    )
    assert user_update.password == "new_password"
    assert user_update.roles == ["admin"]

def test_agent_update_pydantic():
    agent_update = AgentUpdate(
        password="new_password",
        configuration={"key": "new_value"}
    )
    assert agent_update.password == "new_password"
    assert agent_update.configuration == {"key": "new_value"}

def test_third_party_app_update_pydantic():
    app_update = ThirdPartyAppUpdate(
        api_key="new_test_api_key",
        permissions={"key": "new_value"}
    )
    assert app_update.api_key == "new_test_api_key"
    assert app_update.permissions == {"key": "new_value"}

if __name__ == "__main__":
    pytest.main()
