# Need to revisit dependency injection

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db

from services.auth_service import AuthService
from repositories.user_repository import UserRepository
from repositories.refresh_token_repository import RefreshTokenRepository


def get_auth_service(
    db: AsyncSession = Depends(get_db)
) -> AuthService:
    return AuthService(
        db=db,
        user_repository = UserRepository(db),
        refresh_token_repository = RefreshTokenRepository(db)
    )