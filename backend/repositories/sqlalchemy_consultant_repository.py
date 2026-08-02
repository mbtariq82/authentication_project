from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from domain.consultant import Consultant
from models import ConsultantRow
from repositories.abstract_consultant_repository import AbstractConsultantRepository

class SqlAlchemyConsultantRepository(AbstractConsultantRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_domain(row: ConsultantRow) -> Consultant:
        return Consultant(
            id=row.id,
            user_id=row.user_id,
            batch=row.batch,
            placement_status=row.placement_status,
            client=row.client,
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
            .order_by(ConsultantRow.id)
            .offset(offset)
            .limit(limit)
        )
        rows = result.scalars().all()
        consultants = [self._to_domain(row) for row in rows]
        return consultants, total or 0