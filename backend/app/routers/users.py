from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models import User
from app.schemas.user import UserRead, UserCreate

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db, require_role
from app.models import User, FieldJob, FieldJobStatus, Operator, User, User, UserRole, Equipment, EquipmentStatus
from app.schemas.user import UserRead, UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=list[UserRead]) # Response model = schema format that will be returned to the client.
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user), # _ is for a variable you are required to define, but intend to ignore. Requires caller to be logged in with JWT token.
) -> list[User]:

    # Stretch goal, including is_active only
    statement = select(User).where(User.is_active.is_(True)).order_by(User.id)

    result = await db.execute(statement) # Returns a list of database tuples: [(<User object>,), (<User object>,)]
    return list(result.scalars().all())

# Stretch goal "removing objects" by settings is_active to False or whatever
@router.patch("/{user_id}/remove", response_model=UserRead)
async def update_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.FARM_OPERATIONS_ADMIN, UserRole.FIELD_HAND, UserRole.AUDITOR)),
) -> User:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found",
        )
    user.mark_removed()

    # Commit to database.
    await db.commit()
    await db.refresh(user)
    return user

# Bad hardcode, but whatever.
@router.patch("/{user_id}/restore", response_model=UserRead)
async def update_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.FARM_OPERATIONS_ADMIN, UserRole.FIELD_HAND, UserRole.AUDITOR)),
) -> User:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found",
        )
    user.mark_restored()

    # Commit to database.
    await db.commit()
    await db.refresh(user)
    return user