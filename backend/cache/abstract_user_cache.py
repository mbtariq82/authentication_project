from abc import ABC, abstractmethod

from schemas import UserResponse

class AbstractUserCache(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> UserResponse | None:
        raise NotImplementedError

    @abstractmethod
    async def set(self, user: UserResponse) -> None:
        raise NotImplementedError