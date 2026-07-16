from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_username(self, username: str) -> User | None:
        return self.db.scalar(
            select(User).where(User.username == username)
        )