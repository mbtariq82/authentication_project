from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from repositories.abstract_loan_repository import AbstractLoanRepository
from repositories.sqlalchemy_loan_repository import SQLAlchemyLoanRepository
from services.loan_service import LoanService
from unit_of_work.abstract_loan_unit_of_work import AbstractLoanUnitOfWork
from unit_of_work.sqlalchemy_loan_unit_of_work import SqlAlchemyLoanUnitOfWork

async def get_loan_uow(session: AsyncSession = Depends(get_db)) -> AbstractLoanUnitOfWork:
    async with SqlAlchemyLoanUnitOfWork(session) as uow:
        yield uow

def get_loan_repository(session: AsyncSession = Depends(get_db)) -> AbstractLoanRepository:
    return SQLAlchemyLoanRepository(session)

def get_loan_service(uow: AbstractLoanUnitOfWork = Depends(get_loan_uow)) -> LoanService:
    return LoanService(uow)