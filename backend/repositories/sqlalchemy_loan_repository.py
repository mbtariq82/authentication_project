from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.loan import LoanRow
from repositories.abstract_loan_repository import AbstractLoanRepository


class SQLAlchemyLoanRepository(AbstractLoanRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, loan: LoanRow) -> LoanRow:
        self.session.add(loan)
        await self.session.flush()

        return loan

    async def get_loan_by_id(self, loan_id):
        result = await self.session.execute(
            select(LoanRow).where(LoanRow.id == loan_id)
        )
        return result.scalar_one_or_none()

    async def get_loans_by_account_id(self, account_id):
        result = await self.session.execute(
            select(LoanRow).where(
                LoanRow.account_id == account_id,
                LoanRow.current_loan_status.in_(["PENDING", "ACCEPTED"]))
        )
        return list(result.scalars().all())

    async def get_pending_loans(self):
        result = await self.session.execute(
            select(LoanRow).where(LoanRow.current_loan_status == "PENDING")
        )

        return list(result.scalars().all())