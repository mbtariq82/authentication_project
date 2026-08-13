from uuid import UUID

from domain.user import User
from repositories.abstract_user_repository import AbstractUserRepository


class FakeUserRepository(AbstractUserRepository):
    def __init__(self):
        raise NotImplementedError

    async def add(self, user: User) -> User:
        raise NotImplementedError

    async def save(self, user: User) -> User:
        raise NotImplementedError

    async def get_by_id(self, user_id: int) -> User | None:
        raise NotImplementedError

    async def get_by_google_subject(self, google_subject: str) -> User | None:
        raise NotImplementedError
    
    async def get_by_email(self, email: str) -> User | None:
        raise NotImplementedError
