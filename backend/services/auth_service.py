from fastapi import HTTPException   # ideally this should be replaced
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.user_repository import UserRepository
from repositories.refresh_token_repository import RefreshTokenRepository
from security import create_access_token, create_refresh_token, pwd_context

class AuthService:
    def __init__(
        self,
        db: AsyncSession,         # commit should be in the service because of atomicity
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository
    ):
        self.db = db
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository

    async def login(self, username: str, password: str) -> dict[str, str]:
        user = await self.user_repository.get_by_username(username)
        if not user or not pwd_context.verify(password, user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )

        access_token = create_access_token(subject=str(user.id))
        refresh_token, expires_at = create_refresh_token(subject=str(user.id))
        
        await self.refresh_token_repository.create(
            token=refresh_token,
            user_id=user.id,
            expires_at=expires_at
        )

        await self.db.commit()  # this makes sense if you are using multiple repositories

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }