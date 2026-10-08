from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_role
from app.models import User, UserRole
from app.schemas.user import Token, UserCreate, UserRead
from app.security import create_access_token, hash_password, verify_password


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(data={"sub": user.username, "role": user.role.value})
    return Token(access_token=access_token, token_type="bearer")

# require the user to have the Admin role
@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.FARM_OPERATIONS_ADMIN)),
) -> User:
    # check if the username already exists in the db
    existing = await db.execute(select(User).where(func.lower(User.username) == payload.username.lower()))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{payload.username}' is already taken",
        )

    # create a new User object with the provided username, hashed password, and role
    user = User(
        username = payload.username,
        hashed_password=hash_password(payload.password),
        role=payload.role
    )

    # add  new user object to the db
    db.add(user)
    # commit the db transaction
    await db.commit()
    # refresh the user object so that we get the id the db generated
    await db.refresh(user)
    
    return user