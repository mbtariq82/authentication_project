from sqlalchemy import select, func, exists
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from domain.consultant import Consultant
from domain.user import User
from models import ConsultantRow, UserRow
from repositories.abstract_consultant_repository import AbstractConsultantRepository

class SqlAlchemyConsultantRepository(AbstractConsultantRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _consultant_to_domain(
        row: ConsultantRow,
    ) -> Consultant:
        return Consultant(
            id=row.id,
            user_id=row.user_id,
            email=row.user.email,
            first_name=row.user.first_name,
            last_name=row.user.last_name,
            batch=row.batch,
            placement_status=row.placement_status,
            client=row.client,
            created_at=row.created_at,
        )

    @staticmethod
    def _user_to_domain(row: UserRow) -> User:
        return User(
            id=row.id,
            email=row.email,
            first_name=row.first_name,
            last_name=row.last_name,
            role=row.role,
            hashed_password=row.hashed_password,
            google_subject=row.google_subject,
        )
    
    async def list_consultants(
        self,
        offset: int,
        limit: int,
    ) -> tuple[list[Consultant], int]:
        total = await self.session.scalar(
            select(func.count(ConsultantRow.id))
        )
        result = await self.session.execute(
            select(ConsultantRow)
            .options(joinedload(ConsultantRow.user))
            .order_by(
                ConsultantRow.created_at.desc(),
                ConsultantRow.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )
        rows = result.scalars().all()
        consultants = [self._consultant_to_domain(row) for row in rows]
        return consultants, total or 0

    # TODO: move this into the user repository
    async def list_unassigned_users(self) -> list[User]:
        statement = (
            select(UserRow)
            .where(
                ~exists().where(
                    ConsultantRow.user_id == UserRow.id
                )
            )
            .order_by(
                UserRow.first_name,
                UserRow.last_name,
                UserRow.email,
            )
        )
        result = await self.session.execute(statement)
        return [
            self._user_to_domain(row)
            for row in result.scalars().all()
        ]

    async def get_user(self, user_id: int) -> User | None:
        user_row = await self.session.get(UserRow, user_id)
        return self._user_to_domain(user_row) if user_row else None

    async def get_by_user_id(
        self,
        user_id: int,
    ) -> Consultant | None:
        statement = select(ConsultantRow).where(
            ConsultantRow.user_id == user_id
        )
        result = await self.session.execute(statement)
        consultant_row = result.scalar_one_or_none()
        return self._consultant_to_domain(consultant_row) if consultant_row else None

    async def add(
        self,
        consultant: ConsultantRow,
    ) -> Consultant:
        self.session.add(consultant)
        await self.session.flush()
        return self._consultant_to_domain(consultant) if consultant else None

    async def get_with_user(
        self,
        consultant_id: int,
    ) -> Consultant | None:
        statement = (
            select(ConsultantRow)
            .options(joinedload(ConsultantRow.user))
            .where(ConsultantRow.id == consultant_id)
        )
        result = await self.session.execute(statement)
        consultant_row = result.scalar_one_or_none()
        return self._consultant_to_domain(consultant_row) if consultant_row else None