from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from unit_of_work.abstract_user_unit_of_work import AbstractUserUnitOfWork


class SqlAlchemyUserUnitOfWork(AbstractUserUnitOfWork):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self.session_factory = session_factory

    async def __aenter__(self) -> Self:
        self.session = self.session_factory()
        self.users = SqlAlchemyUserRepository(self.session)
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        try:
            if exc_type:
                await self.rollback()
        finally:
            await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
