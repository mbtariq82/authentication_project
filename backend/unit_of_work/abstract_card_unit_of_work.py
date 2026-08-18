from abc import ABC, abstractmethod

from repositories.abstract_card_repository import AbstractCardRepository
from repositories.abstract_user_repository import AbstractUserRepository


class AbstractCardUnitOfWork(ABC):

    card_repository: AbstractCardRepository
    user_repository: AbstractUserRepository

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type:
            await self.rollback()

    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass