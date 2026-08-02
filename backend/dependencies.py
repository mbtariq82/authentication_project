from collections.abc import AsyncIterator
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError
from redis import Redis

from database import async_session_factory
from security import oauth2_scheme, decode_token
from domain.user import User
from schemas import UserResponse
from enums import Role
from exceptions import InvalidAccessTokenError, PermissionDeniedError
from services.auth_service import AuthService
from services.user_service import UserService
from services.consultant_service import ConsultantService
from repositories.abstract_user_repository import AbstractUserRepository
from repositories.abstract_consultant_repository import AbstractConsultantRepository
from repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from repositories.sqlalchemy_consultant_repository import SqlAlchemyConsultantRepository
from redis_client import redis_client
from cache.redis_user_cache import  RedisUserCache
from cache.abstract_user_cache import AbstractUserCache
from rate_limiting.login_rate_limiter import LoginRateLimiter
from unit_of_work.sqlalchemy_auth_unit_of_work import SqlAlchemyAuthUnitOfWork

async def get_db() -> AsyncIterator[AsyncSession]:
    async with async_session_factory() as session:
        yield session

def get_redis() -> Redis:
    return redis_client

def get_user_repository(
    session: AsyncSession = Depends(get_db),
) -> AbstractUserRepository:
    return SqlAlchemyUserRepository(session)

def get_consultant_repository(
    session: AsyncSession = Depends(get_db),
) -> AbstractConsultantRepository:
    return SqlAlchemyConsultantRepository(session)

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
    user_cache: AbstractUserCache = Depends(get_user_cache),
    user_repository: AbstractUserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(cache=user_cache, repository=user_repository)

def get_consultant_service(
    consultant_repository: AbstractConsultantRepository = Depends(get_consultant_repository)
) -> ConsultantService:
    return ConsultantService(repository=consultant_repository)


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