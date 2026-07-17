

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from models import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, 
        token: str, 
        user_id: int,
        expires_at: datetime
    ) -> RefreshToken:
        refresh_token = RefreshToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at
        )
        self.db.add(refresh_token)
        await self.db.flush()

        return refresh_token
