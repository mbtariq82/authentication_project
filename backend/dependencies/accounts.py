from fastapi import Depends
from database import async_session_factory
from services.account_service import AccountService
from unit_of_work.abstract_account_unit_of_work import AbstractAccountUnitOfWork
from unit_of_work.sqlalchemy_account_unit_of_work import SqlAlchemyAccountUnitOfWork

def get_account_unit_of_work() -> AbstractAccountUnitOfWork:
    return SqlAlchemyAccountUnitOfWork(async_session_factory)

def get_account_service(
    unit_of_work: AbstractAccountUnitOfWork = Depends(get_account_unit_of_work),
) -> AccountService:
    return AccountService(unit_of_work)