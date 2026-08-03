from abc import ABC, abstractmethod
from domain.consultant import Consultant
from domain.user import User


class AbstractConsultantRepository(ABC):
    @abstractmethod
    async def list_consultants(self, page: int = 1, page_size: int = 20
    ) -> tuple[list[Consultant], int]:
        raise NotImplementedError

    @abstractmethod
    async def list_unassigned_users(self) -> list[User]:
        raise NotImplementedError

    @abstractmethod
    async def get_user(self, user_id: int) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> Consultant | None:
        raise NotImplementedError
    
    @abstractmethod
    async def add(self, consultant: Consultant) -> Consultant:
        raise NotImplementedError

    @abstractmethod
    async def get_with_user(self, consultant_id: int) -> Consultant | None:
        raise NotImplementedError