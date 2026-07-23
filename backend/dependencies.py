from fastapi import Depends, HTTPException, Request # ideally HTTPException should be replaced with custom handling
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User
from services.auth_service import AuthService
from services.login_rate_limiter import LoginRateLimiter
from repositories.user_repository import UserRepository
from repositories.refresh_token_repository import RefreshTokenRepository
from security import oauth2_scheme
from services.login_rate_limiter import LoginRateLimiter
from redis_client import redis_client

def get_login_rate_limiter() -> LoginRateLimiter:
    return LoginRateLimiter(
        redis=redis_client,
        max_attempts=5,
        window_seconds=60,
    )

async def enforce_login_rate_limit(
    request: Request,
    rate_limiter: LoginRateLimiter = Depends(get_login_rate_limiter),
) -> None:
    client_ip = request.client.host if request.client else "unknown"
    await rate_limiter.check(client_ip)

def get_auth_service(
    db: AsyncSession = Depends(get_db),
) -> AuthService:
    return AuthService(
        db=db,
        user_repository = UserRepository(db),
        refresh_token_repository = RefreshTokenRepository(db),
    )

async def get_current_user(
    access_token: str = Depends(oauth2_scheme),   # swagger authorise box
    service: AuthService = Depends(get_auth_service)
) -> User:
    return await service.authenticate(access_token)