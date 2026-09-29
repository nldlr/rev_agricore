# \backend > python -m scripts.create_tables

import asyncio

from app.database import engine
from app.models import Base

async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("=========Database (SQLAlchemy) reset successfully!=========")

if __name__ == "__main__":
    asyncio.run(create_tables())