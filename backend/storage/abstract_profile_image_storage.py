from abc import ABC, abstractmethod


class AbstractProfileImageStorage(ABC):
    @abstractmethod
    async def save(self, user_id: int, image: bytes) -> str:
        """Store an image and return its durable object key."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_url(self, key: str) -> str:
        """Return a URL suitable for displaying the stored image."""
        raise NotImplementedError
