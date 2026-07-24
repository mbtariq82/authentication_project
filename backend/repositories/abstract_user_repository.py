from abc import ABC, abstractmethod
from models import User

class AbstractUserRepository(ABC):
    @abstractmethod
    async def get_by_username(
        self,
        username: str
    ) -> User | None:
        raise NotImplementedError
    
    @abstractmethod
    async def add(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_google_subject(self, google_subject: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError