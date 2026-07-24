from typing import Self
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from unit_of_work.abstract_user_unit_of_work import AbstractUserUnitOfWork
from cache.abstract_user_cache import AbstractUserCache
from repositories.user_repository import UserRepository

class SqlAlchemyRedisUserUnitOfWork(AbstractUserUnitOfWork):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        user_cache: AbstractUserCache
    ):
        self.session_factory = session_factory
        self.user_cache = user_cache

    async def __aenter__(self) -> Self:
        self.session = self.session_factory()
        self.users = UserRepository(self.session)
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback
    ) -> None:
        try:
            if exc_type:
                await self.rollback()
        finally:
            await self.session.close()