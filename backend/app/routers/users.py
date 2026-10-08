from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models import User
from app.schemas.user import UserRead, UserCreate

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=list[UserRead]) # Response model = schema format that will be returned to the client.
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user), # _ is for a variable you are required to define, but intend to ignore. Requires caller to be logged in with JWT token.
) -> list[User]:
    
    statement = select(User).order_by(User.id)

    result = await db.execute(statement) # Returns a list of database tuples: [(<User object>,), (<User object>,)]
    return list(result.scalars().all())