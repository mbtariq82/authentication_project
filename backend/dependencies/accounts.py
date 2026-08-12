from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from repositories.abstract_account_repository import AbstractAccountRepository
from repositories.sqlalchemy_account_repository import (
    SqlAlchemyAccountRepository,
)
from services.account_service import AccountService


def get_account_repository(
    session: AsyncSession = Depends(get_db),
) -> AbstractAccountRepository:
    return SqlAlchemyAccountRepository(session)


def get_account_service(
    repository: AbstractAccountRepository = Depends(get_account_repository),
) -> AccountService:
    return AccountService(repository)
