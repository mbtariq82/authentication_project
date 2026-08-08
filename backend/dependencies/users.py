from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from cache.abstract_user_cache import AbstractUserCache
from cache.redis_user_cache import RedisUserCache
from dependencies.database import get_db
from dependencies.redis import get_redis
from repositories.abstract_user_repository import AbstractUserRepository
from repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from services.user_service import UserService


def get_user_repository(
    session: AsyncSession = Depends(get_db),
) -> AbstractUserRepository:
    return SqlAlchemyUserRepository(session)


def get_user_cache(
    redis: Redis = Depends(get_redis),
) -> RedisUserCache:
    return RedisUserCache(redis)


def get_user_service(
    user_cache: AbstractUserCache = Depends(get_user_cache),
    user_repository: AbstractUserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(cache=user_cache, repository=user_repository)
