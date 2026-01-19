"""
Author: Yoosuf
Email: mayoosuf@gmail.com
Company: Crew Digital
"""

from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.auth.security import create_access_token, get_password_hash, verify_password
from src.auth.deps import get_current_user
from src.models import User, Role

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)) -> Any:
    # Check if user exists
    stmt = select(User).where(User.email == user_in.email)
    result = await db.execute(stmt)
    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    
    # Check if role exists (default to 'user')
    role_name = user_in.role if user_in.role else "user"
    stmt_role = select(Role).where(Role.name == role_name)
    result_role = await db.execute(stmt_role)
    role_obj = result_role.scalars().first()
    
    if not role_obj:
        raise HTTPException(status_code=400, detail=f"Role '{role_name}' not found")
        
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role_id=role_obj.id
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)) -> Any:
    stmt = select(User).where(User.email == form_data.username)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
