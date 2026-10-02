import asyncio

from app.database import AsyncSessionLocal
from app.models import User, UserRole
from app.security import hash_password

async def seed_users() -> None:
    async with AsyncSessionLocal() as session:
        session.add_all([
            User(username="admin", hashed_password=hash_password("password"), role=UserRole.FARM_OPERATIONS_ADMIN),
            User(username="fieldhand", hashed_password=hash_password("password"), role=UserRole.FIELD_HAND),
            User(username="auditor", hashed_password=hash_password("password"), role=UserRole.AUDITOR),
        ])
        await session.commit()

if __name__ == "__main__":
    asyncio.run(seed_users())