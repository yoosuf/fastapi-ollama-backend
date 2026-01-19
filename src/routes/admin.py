"""
Author: Yoosuf
Email: mayoosuf@gmail.com
Company: Crew Digital
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.auth.deps import PermissionChecker
from src.schemas import UserResponse, PromptResponse
from src.models import User, Prompt

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(PermissionChecker("users:read")),
    db: AsyncSession = Depends(get_db)
):
    """Admin only: List all users"""
    query = select(User).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/all-prompts", response_model=List[PromptResponse])
async def get_all_prompts(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(PermissionChecker("prompts:read_all")),
    db: AsyncSession = Depends(get_db)
):
    """Admin only: View prompts from all users for auditing"""
    query = select(Prompt).order_by(Prompt.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
