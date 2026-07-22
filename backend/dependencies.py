# Need to revisit dependency injection

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User
from services.auth_service import AuthService
from repositories.user_repository import UserRepository
from repositories.refresh_token_repository import RefreshTokenRepository
from security import oauth2_scheme
from services.login_rate_limiter import LoginRateLimiter
from redis_client import redis_client

def get_login_rate_limiter() -> LoginRateLimiter:
    return LoginRateLimiter(redis_client)

def get_auth_service(
    db: AsyncSession = Depends(get_db),
    login_rate_limiter: LoginRateLimiter = Depends(
        get_login_rate_limiter
    )
) -> AuthService:
    return AuthService(
        db=db,
        user_repository = UserRepository(db),
        refresh_token_repository = RefreshTokenRepository(db)
    )

async def get_current_user(
    access_token: str = Depends(oauth2_scheme),   # swagger authorise box
    service: AuthService = Depends(get_auth_service)
) -> User:
    return await service.authenticate(access_token)