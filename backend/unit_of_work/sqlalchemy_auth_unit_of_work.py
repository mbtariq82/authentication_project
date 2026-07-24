from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing import Self

from repositories.user_repository import UserRepository
from repositories.refresh_token_repository import RefreshTokenRepository
from unit_of_work.abstract_auth_unit_of_work import AbstractAuthUnitOfWork

class SqlAlchemyAuthUnitOfWork(AbstractAuthUnitOfWork):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession]
    ):
        self.session_factory = session_factory

    async def __aenter__(self) -> Self:
        self.session = self.session_factory()
        self.users = UserRepository(self.session)
        self.refresh_tokens = RefreshTokenRepository(self.session)
        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback
    ) -> None:
        try:
            await self.rollback()
        finally:
            await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()