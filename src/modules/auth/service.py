from datetime import timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.config import settings
from src.core.database import get_db
from src.modules.auth.models import Role, User
from src.modules.auth.schemas import Token, TokenData, UserCreate
from src.modules.auth.utils import create_access_token, get_password_hash, verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def register_new_user(user_in: UserCreate, db: AsyncSession) -> User:
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
        role_id=role_obj.id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(form_data, db: AsyncSession) -> Token:
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
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")


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
        raise credentials_exception from None

    query = select(User).where(User.email == token_data.email)
    result = await db.execute(query)
    user = result.scalars().first()

    if user is None:
        raise credentials_exception
    return user


async def get_current_user_with_permissions(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> User:
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
                detail="User has no role assigned",
            )

        # Check if user has the specific permission
        user_permissions = [p.name for p in user.role.permissions]
        if self.required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Missing permission: {self.required_permission}",
            )
        return user
