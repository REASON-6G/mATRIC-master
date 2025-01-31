from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import DatabaseManager
from ..dependencies import get_db
from ..models import UserCreate, UserUpdate, TokenData
from ..auth import get_current_user, auth_manager

router = APIRouter()

# public endpoint to create the first user
@router.post("/public", response_model=TokenData)
async def create_first_user(user: UserCreate, db: Session = Depends(get_db)):
    db_manager = DatabaseManager(db)
    existing_user = db_manager.get_user(user.username)
    #print("existing_user: ", existing_user)
    if existing_user:
        raise HTTPException(status_code=400, detail="username already registered")
    password_hash = auth_manager.hash_password(user.password)
    #print("password_hash: ", password_hash)
    new_user = db_manager.add_user(user.username, password_hash, user.roles)
    #print("new_user: ", new_user)
    if not new_user:
        raise HTTPException(status_code=400, detail="user creation failed")
    return new_user

@router.post("/", response_model=TokenData)
async def create_user(user: UserCreate, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    if 'admin' not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create users")
    
    db_manager = DatabaseManager(db)
    existing_user = db_manager.get_user(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    password_hash = auth_manager.hash_password(user.password)
    new_user = db_manager.add_user(user.username, password_hash, user.roles)
    if not new_user:
        raise HTTPException(status_code=400, detail="User creation failed")
    return new_user

@router.put("/{username}", response_model=TokenData)
async def update_user(username: str, user: UserUpdate, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    if 'admin' not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update users")
    
    db_manager = DatabaseManager(db)
    password_hash = auth_manager.hash_password(user.password)
    updated_user = db_manager.update_user(username, password_hash, user.roles)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/{username}", response_model=dict)
async def delete_user(username: str, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    if 'admin' not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete users")
    
    db_manager = DatabaseManager(db)
    success = db_manager.delete_user(username)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "detail": f"User {username} deleted"}

@router.get("/me", response_model=TokenData)
async def read_users_me(current_user: TokenData = Depends(get_current_user)):
    return current_user

@router.get("/{username}", response_model=TokenData)
async def get_user(username: str, db: Session = Depends(get_db)):
    db_manager = DatabaseManager(db)
    user = db_manager.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=List[TokenData])
async def list_users(db: Session = Depends(get_db)):
    db_manager = DatabaseManager(db)
    users = db_manager.get_all_users()
    return users
