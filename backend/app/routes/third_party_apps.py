from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..models import ThirdPartyAppCreate, ThirdPartyAppUpdate, ThirdPartyApp, TokenData
from ..database import DatabaseManager
from ..dependencies import get_db

router = APIRouter()

@router.post("/", response_model=ThirdPartyApp)
async def create_third_party_app(app: ThirdPartyAppCreate, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    if 'admin' not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create third-party apps")
    db_manager = DatabaseManager(db)
    new_app = db_manager.add_third_party_app(app.app_name, app.api_key, app.permissions)
    if not new_app:
        raise HTTPException(status_code=400, detail="Third-party app_old creation failed")
    return new_app

@router.get("/{app_name}", response_model=ThirdPartyApp)
async def get_third_party_app(app_name: str, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    if 'admin' not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create third-party apps")
    db_manager = DatabaseManager(db)
    app = db_manager.get_third_party_app(app_name)
    if not app:
        raise HTTPException(status_code=404, detail="Third-party app_old not found")
    return app

@router.put("/{app_name}", response_model=ThirdPartyApp)
async def update_third_party_app(app_name: str, app: ThirdPartyAppUpdate, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    if 'admin' not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update third-party apps")
    db_manager = DatabaseManager(db)
    updated_app = db_manager.update_third_party_app(app_name, app.api_key, app.permissions)
    if not updated_app:
        raise HTTPException(status_code=404, detail="Third-party app_old not found")
    return updated_app

@router.delete("/{app_name}", response_model=dict)
async def delete_third_party_app(app_name: str, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    if 'admin' not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete third-party apps")
    db_manager = DatabaseManager(db)
    success = db_manager.delete_third_party_app(app_name)
    if not success:
        raise HTTPException(status_code=404, detail="Third-party app_old not found")
    return {"status": "success", "detail": f"Third-party app_old {app_name} deleted"}
