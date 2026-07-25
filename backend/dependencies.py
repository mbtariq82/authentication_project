from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError
from redis import Redis

from database import async_session_factory
from security import oauth2_scheme, decode_token
from models import User
from schemas import UserResponse
from enums import Role
from exceptions import InvalidAccessTokenError, PermissionDeniedError
from services.auth_service import AuthService
from services.user_service import UserService
from redis_client import redis_client
from cache.redis_user_cache import  RedisUserCache
from cache.abstract_user_cache import AbstractUserCache
from rate_limiting.login_rate_limiter import LoginRateLimiter
from unit_of_work.sqlalchemy_auth_unit_of_work import SqlAlchemyAuthUnitOfWork
from unit_of_work.sqlalchemy_redis_user_unit_of_work import SqlAlchemyRedisUserUnitOfWork

def get_redis() -> Redis:
    return redis_client

# Cache and Rate Limiting
def get_login_rate_limiter(
    redis: Redis = Depends(get_redis)
) -> LoginRateLimiter:
    return LoginRateLimiter(
        redis=redis,
        max_attempts=3,
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
) ->  RedisUserCache:
    return  RedisUserCache(redis)

# Services
def get_auth_service() -> AuthService:
    uow = SqlAlchemyAuthUnitOfWork(async_session_factory) # TODO: create separate dependency for uow
    return AuthService(uow)

def get_user_service(
    user_cache: AbstractUserCache = Depends(get_user_cache)
) -> UserService:
    uow = SqlAlchemyRedisUserUnitOfWork( # TODO: create separate dependency for uow
        session_factory=async_session_factory,
        user_cache=user_cache
    )
    return UserService(uow)


async def get_current_user(
    access_token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
) -> User:
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

async def require_admin(
    user: User = Depends(get_current_user)
) -> User:
    if user.role != Role.ADMIN:
        raise PermissionDeniedError()
    return user