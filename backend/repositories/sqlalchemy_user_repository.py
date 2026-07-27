from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.user import User
from models import UserRow
from repositories.abstract_user_repository import AbstractUserRepository

class SqlAlchemyUserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_domain(row: UserRow) -> User:
        return User(
            id=row.id,
            email=row.email,
            role=row.role,
            hashed_password=row.hashed_password,
            google_subject=row.google_subject,
        )

    async def add(self, user: User) -> User:
        row = UserRow(
            email=user.email,
            role=user.role,
            hashed_password=user.hashed_password,
            google_subject=user.google_subject,
        )
        self.session.add(row)
        await self.session.flush() # we need User.id
        return self._to_domain(row)

    async def save(self, user: User) -> User:
        if user.id is None:
            raise ValueError("Cannot save a user without an ID")
        row = await self.session.get(UserRow, user.id)
        if not row:
            raise ValueError(f"User with id {user.id} not found")
        row.email = user.email
        row.role = user.role
        row.hashed_password = user.hashed_password
        row.google_subject = user.google_subject
        await self.session.flush()
        return self._to_domain(row)

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(
            select(UserRow).where(UserRow.id == user_id)
        )
        row = result.scalar_one_or_none()
        return self._to_domain(row) if row else None
    
    async def get_by_google_subject(self, google_subject: str) -> User | None:
        result = await self.session.execute(
            select(UserRow).where(UserRow.google_subject == google_subject)
        )
        row = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(UserRow).where(UserRow.email == email)
        )
        row = result.scalar_one_or_none()
        return self._to_domain(row) if row else None