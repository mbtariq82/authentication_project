from abc import ABC, abstractmethod
from datetime import datetime

from models import RefreshToken, User

class AbstractRefreshTokenRepository(ABC):
    @abstractmethod
    async def add(self, token: str, user_id: int,expires_at: datetime) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_token(self, token: str) -> RefreshToken | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, refresh_token: RefreshToken) -> None:
        raise NotImplementedError