

from datetime import datetime
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import RefreshToken, User


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, token: str, user_id: int,expires_at: datetime) -> None:
        refresh_token = RefreshToken(token=token, user_id=user_id, expires_at=expires_at)
        self.db.add(refresh_token)
    
    async def get_by_token(self, token: str) -> RefreshToken | None:
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, refresh_token: RefreshToken) -> None:
        await self.db.delete(refresh_token)

    async def delete_by_token(self, token: str) -> None:
        await self.db.execute(
            delete(RefreshToken).where(RefreshToken.token == token)
        )

    async def delete_by_user_id(self, user_id: int) -> None:
        await self.db.execute(
            delete(RefreshToken).where(RefreshToken.user_id == user_id)
        )

    async def delete_expired(self) -> None:
        await self.db.execute(
            delete(RefreshToken).where(
                RefreshToken.expires_at < datetime.now(timezone.utc)
            )
        )
        
