from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.user import User
from models.user import UserRow
from repositories.abstract_user_repository import AbstractUserRepository


class SqlAlchemyUserRepository(AbstractUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_domain(row: UserRow) -> User:
        return User(
            id=row.id,
            email=row.email,
            first_name=row.first_name,
            last_name=row.last_name,
            role=row.role,
            hashed_password=row.hashed_password,
            google_subject=row.google_subject,
            profile_image_key=row.profile_image_key,
            phone=row.mobile,
            address=row.address_line,
            dob=row.dob,
            postcode=row.postcode,
            country=row.country,
            city=row.city,
        )
    
    @staticmethod
    def _apply_domain(row: UserRow, user: User) -> None:
        row.email = user.email
        row.first_name = user.first_name
        row.last_name = user.last_name
        row.role = user.role
        row.hashed_password = user.hashed_password
        row.google_subject = user.google_subject
        row.profile_image_key = user.profile_image_key
        row.mobile = user.phone
        row.address_line = user.address
        row.dob = user.dob
        row.postcode = user.postcode
        row.country = user.country
        row.city = user.city

    async def add(self, user: User) -> User:
        row = UserRow(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            hashed_password=user.hashed_password,
            google_subject=user.google_subject,
            profile_image_key=user.profile_image_key,
            mobile=user.phone,
            address_line=user.address,
            dob=user.dob,
            postcode=user.postcode,
            country=user.country,
            city=user.city,
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
        self._apply_domain(row, user)
        await self.session.flush()
        return self._to_domain(row)

    async def get_by_id(self, user_id: int) -> User | None:
        row = await self.session.get(UserRow, user_id)
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
