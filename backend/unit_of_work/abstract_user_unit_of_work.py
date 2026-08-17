from abc import ABC, abstractmethod
from typing import Self

from repositories.abstract_user_repository import AbstractUserRepository


class AbstractUserUnitOfWork(ABC):
    users: AbstractUserRepository

    @abstractmethod
    async def __aenter__(self) -> Self:
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError
