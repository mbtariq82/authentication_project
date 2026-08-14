from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing import Self

from repositories.sqlalchemy_account_repository import SqlAlchemyAccountRepository
from unit_of_work.abstract_account_unit_of_work import AbstractAccountUnitOfWork


class SqlAlchemyAccountUnitOfWork(AbstractAccountUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def __aenter__(self) -> Self:
        self.session = self.session_factory()
        self.accounts = SqlAlchemyAccountRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        try:
            if exc_type:
                await self.rollback()
        finally:
            await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()