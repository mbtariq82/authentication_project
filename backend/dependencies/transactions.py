from collections.abc import AsyncIterator

from fastapi import Depends
from database import async_session_factory
from unit_of_work.abstract_transaction_unit_of_work import (
    AbstractTransactionUnitOfWork,
)
from unit_of_work.sqlalchemy_transaction_unit_of_work import (
    SqlAlchemyTransactionUnitOfWork,
)
from services.transaction_service import TransactionService


async def get_transaction_unit_of_work() -> AsyncIterator[AbstractTransactionUnitOfWork]:
    async with SqlAlchemyTransactionUnitOfWork(async_session_factory) as unit_of_work:
        yield unit_of_work


def get_transaction_service(
    unit_of_work: AbstractTransactionUnitOfWork = Depends(
        get_transaction_unit_of_work
    ),
) -> TransactionService:
    return TransactionService(unit_of_work)