import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy import select
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from .database import AsyncSessionLocal
from app.models import User, UserRole
from app.security import decode_access_token

# Provides db session for API routers.
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# Defines where to login to obtain Bearer token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Validates JWT (Json Web Token) - Bearer token (OAuth2)
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    # 1. ^ Extract Token and Session

    # 2. Define 401 unauthorized exception.
    credentials_exception= HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = decode_access_token(token) # Parse JWT payload.
        username = payload.get("sub") # Checks for subject claim (which stores username, can't be missing/invalid).
        if username is None:
            raise credentials_exception
    # except jwt.InvalidTokenError:
    except jwt.PyJWTError:
        raise credentials_exception

    # Execute SQLAlchemy query for user.
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user # Return ORM object.

# Restricts endpoint access via user roles.
def require_role(*allowed_roles: UserRole): # Higher-order dependency function, idk.
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, # 403 Forbidden Error
                detail=(
                    f"Role '{current_user.role.value}' is not permitted to perform this action"
                ),
            )
        return current_user
    return role_checker