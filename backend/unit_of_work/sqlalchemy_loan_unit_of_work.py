from sqlalchemy.ext.asyncio import AsyncSession

from repositories.abstract_loan_repository import AbstractLoanRepository
from repositories.sqlalchemy_loan_repository import SQLAlchemyLoanRepository
from unit_of_work.abstract_loan_unit_of_work import AbstractLoanUnitOfWork


class SqlAlchemyLoanUnitOfWork(AbstractLoanUnitOfWork):

    def __init__(self, session: AsyncSession):
        self.session = session
        self.loans: AbstractLoanRepository = SQLAlchemyLoanRepository(session)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()