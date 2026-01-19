from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.config import settings
from src.database import get_db
from src.models import User, Role
from src.schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
        
    query = select(User).where(User.email == token_data.email)
    result = await db.execute(query)
    user = result.scalars().first()
    
    if user is None:
        raise credentials_exception
    return user

    if user is None:
        raise credentials_exception
    return user

async def get_current_user_with_permissions(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> User:
    # Eager load role and permissions
    # In async sqlalchemy, relationship loading requires explicit query or joinedload options if not lazy='joined'
    # But for simplicity, we can just re-query or rely on lazy loading if strictly async-safe config is on.
    # A safe bet is explicitly loading them.
    from sqlalchemy.orm import selectinload
    
    query = select(User).options(selectinload(User.role).selectinload(Role.permissions)).where(User.id == user.id)
    result = await db.execute(query)
    user_with_perms = result.scalars().first()
    return user_with_perms

class PermissionChecker:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    async def __call__(self, user: User = Depends(get_current_user_with_permissions)) -> User:
        if not user.role:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="User has no role assigned"
            )
            
        # Check if user has the specific permission
        user_permissions = [p.name for p in user.role.permissions]
        if self.required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Operation not permitted. Missing permission: {self.required_permission}"
            )
        return user
