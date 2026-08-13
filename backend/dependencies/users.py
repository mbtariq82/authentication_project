from fastapi import Depends
from redis.asyncio import Redis

from cache.abstract_user_cache import AbstractUserCache
from cache.redis_user_cache import RedisUserCache
from database import async_session_factory
from dependencies.profile_images import get_profile_image_storage
from dependencies.redis import get_redis
from services.user_service import UserService
from storage.abstract_profile_image_storage import AbstractProfileImageStorage
from unit_of_work.sqlalchemy_user_unit_of_work import SqlAlchemyUserUnitOfWork


def get_user_cache(
    redis: Redis = Depends(get_redis),
) -> RedisUserCache:
    return RedisUserCache(redis)


def get_user_service(
    user_cache: AbstractUserCache = Depends(get_user_cache),
    image_storage: AbstractProfileImageStorage = Depends(
        get_profile_image_storage
    ),
) -> UserService:
    return UserService(
        cache=user_cache,
        uow=SqlAlchemyUserUnitOfWork(async_session_factory),
        image_storage=image_storage,
    )
