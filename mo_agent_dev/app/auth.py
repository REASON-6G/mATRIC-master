from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from .config import settings
from .database import DatabaseManager, get_db_manager
from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi.security import OAuth2PasswordBearer
from .dependencies import get_db
from .models import UserCreate, UserUpdate, Token, TokenData  # Assuming these are in models.py

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class AuthManager:
    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password):
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        if "sub" not in to_encode:
            raise ValueError("Token data should include sub field")

        encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        print("encoded_jwt: ", encoded_jwt)
        return encoded_jwt

    def authenticate_user(self, username: str, password: str, db_manager: DatabaseManager):
        user = db_manager.get_user(username)
        if not user:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user

    def authenticate_onboard_agent(self, username: str, password: str, db_manager: DatabaseManager):
        agent = db_manager.get_agent_by_username(username)
        if agent and self.verify_password(password, agent.password_hash):
            if agent.onboard:
                return agent
            else:
                agent.onboard = True
                db_manager.update_agent_onboard_status(agent)
                return agent
        return None

    def authenticate_third_party_app(self, app_name: str, api_key: str, db_manager: DatabaseManager):
        app = db_manager.get_third_party_app(app_name)
        if not app or app.api_key != api_key:
            return None
        return app

    def get_current_user(self, token: str, db_manager: DatabaseManager):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            print("decoded payload: ", payload)
            username: str = payload.get("sub")
            print("username: ", username)
            if username is None:
                raise credentials_exception
        except JWTError as e:
            print("JWTError: ", str(e))
            raise credentials_exception
        user = db_manager.get_user(username)
        if user is None:
            raise credentials_exception
        return user

auth_manager = AuthManager()

# Dependency to get the current user
def get_current_user(token: str = Depends(oauth2_scheme), db: DatabaseManager = Depends(get_db_manager))-> TokenData:
    return auth_manager.get_current_user(token, db)
