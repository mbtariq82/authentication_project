from abc import ABC, abstractmethod
from typing import Self

from repositories.abstract_user_repository import AbstractUserRepository
from repositories.abstract_refresh_token_repository import AbstractRefreshTokenRepository

class AbstractAuthUnitOfWork(ABC):
    users: AbstractUserRepository
    refresh_tokens: AbstractRefreshTokenRepository

    # we need __aenter__ and __aexit__ so that we can do:
    # async with self.unit_of_work as uow
    @abstractmethod
    async def __aenter__(self) -> Self:
        raise NotImplementedError
    
    @abstractmethod
    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError
