from abc import ABC, abstractmethod
from typing import Self

from repositories.abstract_account_repository import AbstractAccountRepository


class AbstractAccountUnitOfWork(ABC):
    accounts: AbstractAccountRepository

    @abstractmethod
    async def __aenter__(self) -> Self:
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError