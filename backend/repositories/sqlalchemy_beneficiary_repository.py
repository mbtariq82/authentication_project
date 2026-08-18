from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.beneficiary import Beneficiary
from models.beneficiary import BeneficiaryRow
from repositories.abstract_beneficiary_repository import (
    AbstractBeneficiaryRepository,
)


class SqlAlchemyBeneficiaryRepository(AbstractBeneficiaryRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_domain(row: BeneficiaryRow) -> Beneficiary:
        return Beneficiary(
            id=row.id,
            user_id=row.user_id,
            name=row.name,
            account_number=row.account_number,
            sort_code=row.sort_code,
            bank_name=row.bank_name,
            reference=row.reference,
            is_active=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    async def add(self, beneficiary: Beneficiary) -> Beneficiary:
        row = BeneficiaryRow(
            user_id=beneficiary.user_id,
            name=beneficiary.name,
            account_number=beneficiary.account_number,
            sort_code=beneficiary.sort_code,
            bank_name=beneficiary.bank_name,
            reference=beneficiary.reference,
            is_active=beneficiary.is_active,
        )
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return self._to_domain(row)

    async def list_by_user(
        self,
        user_id: int,
        *,
        include_inactive: bool = False,
    ) -> list[Beneficiary]:
        statement = select(BeneficiaryRow).where(
            BeneficiaryRow.user_id == user_id
        )
        if not include_inactive:
            statement = statement.where(BeneficiaryRow.is_active.is_(True))
        statement = statement.order_by(BeneficiaryRow.name, BeneficiaryRow.id)
        result = await self.session.execute(statement)
        return [self._to_domain(row) for row in result.scalars().all()]

    async def get_by_id(
        self,
        beneficiary_id: int,
        user_id: int,
    ) -> Beneficiary | None:
        result = await self.session.execute(
            select(BeneficiaryRow).where(
                BeneficiaryRow.id == beneficiary_id,
                BeneficiaryRow.user_id == user_id,
            )
        )
        row = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def update(
        self,
        beneficiary_id: int,
        user_id: int,
        changes: dict[str, object],
    ) -> Beneficiary | None:
        result = await self.session.execute(
            select(BeneficiaryRow).where(
                BeneficiaryRow.id == beneficiary_id,
                BeneficiaryRow.user_id == user_id,
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None

        for field, value in changes.items():
            if field in {
                "name",
                "account_number",
                "sort_code",
                "bank_name",
                "reference",
                "is_active",
            }:
                setattr(row, field, value)

        await self.session.commit()
        await self.session.refresh(row)
        return self._to_domain(row)

    async def deactivate(
        self,
        beneficiary_id: int,
        user_id: int,
    ) -> Beneficiary | None:
        return await self.update(
            beneficiary_id,
            user_id,
            {"is_active": False},
        )
