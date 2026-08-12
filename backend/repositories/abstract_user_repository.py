from abc import ABC, abstractmethod

from domain.user import User

class AbstractUserRepository(ABC):    
    @abstractmethod
    async def add(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def save(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError
