

from datetime import datetime, timezone
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import RefreshToken, User


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, token: str, user_id: int,expires_at: datetime) -> None:
        refresh_token = RefreshToken(token=token, user_id=user_id, expires_at=expires_at)
        self.db.add(refresh_token)
    
    async def get_by_token(self, token: str) -> RefreshToken | None:
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        return result.scalar_one_or_none()

    async def delete(self, refresh_token: RefreshToken) -> None:
        await self.db.delete(refresh_token)
