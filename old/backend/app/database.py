from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from .config import settings
from .models import User as UserModel, UserCreate, UserUpdate
from .models import Agents as AgentModel
from .models import ThirdPartyApps as ThirdPartyAppModel
#from .database_session import SessionLocal, Base
from app.models import AgentCommand  # For conflict resolution
from datetime import datetime
from .dependencies import get_db


def get_db_manager(db: Session = Depends(get_db)):
    return DatabaseManager(db)

class DatabaseManager:
    def __init__(self, db: Session):
        self.db = db

    # User operations
    def get_user(self, username: str):
        return self.db.query(UserModel).filter(UserModel.username == username).first()

    def add_user(self, username: str, password_hash: str, roles: list):
        new_user = UserModel(username=username, password_hash=password_hash, roles=roles)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def update_user(self, username: str, password_hash: str = None, roles: list = None):
        user = self.get_user(username)
        if not user:
            return None
        if password_hash:
            user.password_hash = password_hash
        if roles:
            user.roles = roles
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, username: str):
        user = self.get_user(username)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False

    def get_all_users(self):
        return self.db.query(UserModel).all()

    # Agent operations
    def get_agent(self, ap_id: str):
        return self.db.query(AgentModel).filter(AgentModel.ap_id == ap_id).first()

    def get_agent_by_username(self, username: str):
        return self.db.query(AgentModel).filter(AgentModel.ap_id == username).first()

    def add_agent(self, ap_id: str, password_hash: str, configuration: dict):
        new_agent = AgentModel(ap_id=ap_id, password_hash=password_hash, configuration=configuration, onboard=False)
        self.db.add(new_agent)
        self.db.commit()
        self.db.refresh(new_agent)
        return new_agent

    def update_agent(self, ap_id: str, configuration: dict = None, supported_commands: list = None):
        agent = self.get_agent(ap_id)
        if not agent:
            return None
        if configuration:
            agent.configuration = configuration
        if supported_commands:
            agent.supported_commands = supported_commands
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def delete_agent(self, ap_id: str):
        agent = self.get_agent(ap_id)
        if agent:
            self.db.delete(agent)
            self.db.commit()
            return True
        return False

    def update_agent_onboard_status(self, agent: AgentModel):
        self.db.commit()
        self.db.refresh(agent)

    def get_all_agents(self):
        return self.db.query(AgentModel).all()

    # Third-party app operations
    def get_third_party_app(self, app_name: str):
        return self.db.query(ThirdPartyAppModel).filter(ThirdPartyAppModel.app_name == app_name).first()

    def add_third_party_app(self, app_name: str, api_key: str, permissions: dict):
        new_app = ThirdPartyAppModel(app_name=app_name, api_key=api_key, permissions=permissions)
        self.db.add(new_app)
        self.db.commit()
        self.db.refresh(new_app)
        return new_app

    def update_third_party_app(self, app_name: str, api_key: str = None, permissions: dict = None):
        app = self.get_third_party_app(app_name)
        if not app:
            return None
        if api_key:
            app.api_key = api_key
        if permissions:
            app.permissions = permissions
        self.db.commit()
        self.db.refresh(app)
        return app

    def delete_third_party_app(self, app_name: str):
        app = self.get_third_party_app(app_name)
        if app:
            self.db.delete(app)
            self.db.commit()
            return True
        return False

    def get_all_third_party_apps(self):
        return self.db.query(ThirdPartyAppModel).all()


    # Conflict resolution operations (new)
    def get_last_command_for_agent(self, agent_id: str):
        """
        Retrieves the last command sent to a specific agent from the database.
        """
        return self.db.query(AgentCommand)\
            .filter(AgentCommand.agent_id == agent_id)\
            .order_by(AgentCommand.timestamp.desc())\
            .first()

    def save_command_for_agent(self, agent_id: str, command: str):
        """
        Saves a new command sent to the agent into the database.
        """
        now = datetime.utcnow()
        new_command = AgentCommand(
            agent_id=agent_id,
            timestamp=now,
            command=command
        )
        print("before db add")
        self.db.add(new_command)
        print("after db add")
        self.db.commit()
