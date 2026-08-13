from database import async_session_factory
from services.account_service import AccountService
from unit_of_work.sqlalchemy_account_unit_of_work import (
    SqlAlchemyAccountUnitOfWork,
)


def get_account_service() -> AccountService:
    unit_of_work = SqlAlchemyAccountUnitOfWork(async_session_factory)
    return AccountService(unit_of_work)