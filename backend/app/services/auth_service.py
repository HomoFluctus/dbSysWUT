from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import (create_access_token, create_refresh_token,
                                decode_token, get_password_hash,
                                verify_password)
from app.models.category import Category
from app.models.user import User
from app.schemas.user import TokenResponse, UserRegister


async def register_user(db: AsyncSession, data: UserRegister) -> TokenResponse:
    existing = await db.execute(
        select(User).where((User.username == data.username) | (User.email == data.email))
    )
    if existing.scalar_one_or_none():
        raise ConflictError("Username or email already exists")

    user = User(
        username=data.username,
        email=data.email,
        password_hash=get_password_hash(data.password),
    )
    db.add(user)
    await db.flush()

    # Create default category
    default_cat = Category(user_id=user.user_id, name="默认", color="#6366f1", is_default=True)
    db.add(default_cat)
    await db.flush()

    access_token = create_access_token({"sub": str(user.user_id)})
    refresh_token = create_refresh_token({"sub": str(user.user_id)})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def login_user(db: AsyncSession, username: str, password: str) -> TokenResponse:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise UnauthorizedError("Invalid username or password")

    access_token = create_access_token({"sub": str(user.user_id)})
    refresh_token = create_refresh_token({"sub": str(user.user_id)})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> TokenResponse:
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")
        user_id = payload.get("sub")
    except Exception:
        raise UnauthorizedError("Invalid refresh token")

    result = await db.execute(select(User).where(User.user_id == int(user_id)))
    if not result.scalar_one_or_none():
        raise UnauthorizedError("User not found")

    new_access = create_access_token({"sub": str(user_id)})
    new_refresh = create_refresh_token({"sub": str(user_id)})
    return TokenResponse(access_token=new_access, refresh_token=new_refresh)
