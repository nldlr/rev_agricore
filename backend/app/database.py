import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    # Put your own database url here with your password
    # EX: postgreql+asyncpg://<yourusername>:<yourpassword>@localhost:5432/robopulse_dev_2478
    "postgresql+asyncpg://postgres:postgres@localhost:5432/agricore_db"
)

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)