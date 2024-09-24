from fastapi import APIRouter, Depends, HTTPException, status, Query
from starlette.requests import Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from ..config import settings
from ..auth import auth_manager
from ..models import Token
from ..database import DatabaseManager
from ..dependencies import get_db

router = APIRouter()


@router.post("/", response_model=Token)
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db),
                login_type: str = Query(..., description="Login type: user, agent or third_party_app")):
    db_manager = DatabaseManager(db)

    login_type = request.query_params.get('login_type')
    if not login_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Login type is required")

    if login_type == "user":
        user = auth_manager.authenticate_user(form_data.username, form_data.password, db_manager)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = auth_manager.create_access_token(
            data={"sub": user.username, "scope": "user"}, expires_delta=access_token_expires
        )
    elif login_type == "agent":
        user = auth_manager.authenticate_onboard_agent(form_data.username, form_data.password, db_manager)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect agent credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = auth_manager.create_access_token(
            data={"sub": user.ap_id, "scope": "agent"}, expires_delta=access_token_expires
        )
    elif login_type == "third_party_app":
        app = auth_manager.authenticate_third_party_app(form_data.username, form_data.password, db_manager)
        if not app:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect API ID or API key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = auth_manager.create_access_token(
            data={"sub": app.app_name, "scope": "third_party_app"}, expires_delta=access_token_expires
        )
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid login type")

    expires_in = int(access_token_expires.total_seconds())
    print("expires_in: ", expires_in)
    return {"access_token": access_token, "token_type": "bearer", "expires_in": int(access_token_expires.total_seconds())}
