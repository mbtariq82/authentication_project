from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError
from redis import Redis

from database import async_session
from security import oauth2_scheme, decode_token
from schemas import UserResponse
from exceptions import InvalidAccessTokenError
from services.auth_service import AuthService
from services.user_service import UserService
from repositories.user_repository import UserRepository
from repositories.refresh_token_repository import RefreshTokenRepository
from redis_client import redis_client
from cache.user_cache import UserCache
from rate_limiting.login_rate_limiter import LoginRateLimiter

# Databases
async def get_db():
    async with async_session() as session:
        yield session

def get_redis() -> Redis:
    return redis_client

# Cache and Rate Limiting
def get_login_rate_limiter(
    redis: Redis = Depends(get_redis)
) -> LoginRateLimiter:
    return LoginRateLimiter(
        redis=redis,
        max_attempts=5,
        window_seconds=60,
    )

async def enforce_login_rate_limit(
    request: Request,
    rate_limiter: LoginRateLimiter = Depends(get_login_rate_limiter),
) -> None:
    client_ip = request.client.host if request.client else "unknown"
    await rate_limiter.check(client_ip)

def get_user_cache(
    redis: Redis = Depends(get_redis)
) -> UserCache:
    return UserCache(redis)

# Services
def get_auth_service(
    db: AsyncSession = Depends(get_db),
) -> AuthService:
    return AuthService(
        db=db,
        user_repository = UserRepository(db),
        refresh_token_repository = RefreshTokenRepository(db),
    )

def get_user_service(
    db: AsyncSession = Depends(get_db),
    user_cache: UserCache = Depends(get_user_cache)
) -> UserService:
    return UserService(
        user_repository=UserRepository(db),
        user_cache=user_cache
    )

# authentication
async def get_current_user(
    access_token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    try:
        payload = decode_token(access_token)
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError) as exc:
        raise InvalidAccessTokenError() from exc
    if payload.get("type") != "access":
        raise InvalidAccessTokenError()
    user = await user_service.get_by_id(user_id)
    if not user:
        raise InvalidAccessTokenError()
    return user