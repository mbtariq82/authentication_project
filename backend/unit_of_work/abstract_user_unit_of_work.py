from abc import ABC, abstractmethod
from typing import Self

from repositories.abstract_user_repository import AbstractUserRepository
from cache.abstract_user_cache import AbstractUserCache

class AbstractUserUnitOfWork(ABC):
    users: AbstractUserRepository
    user_cache: AbstractUserCache

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

    