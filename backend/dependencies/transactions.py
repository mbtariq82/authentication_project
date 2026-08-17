from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from repositories.abstract_account_repository import AbstractAccountRepository
from repositories.abstract_beneficiary_repository import (
    AbstractBeneficiaryRepository,
)
from repositories.abstract_transaction_repository import (
    AbstractTransactionRepository,
)
from repositories.sqlalchemy_account_repository import SqlAlchemyAccountRepository
from repositories.sqlalchemy_beneficiary_repository import (
    SqlAlchemyBeneficiaryRepository,
)
from repositories.sqlalchemy_transaction_repository import (
    SqlAlchemyTransactionRepository,
)
from services.transaction_service import TransactionService


def get_transaction_service(
    session: AsyncSession = Depends(get_db),
) -> TransactionService:
    transaction_repository: AbstractTransactionRepository = (
        SqlAlchemyTransactionRepository(session)
    )
    account_repository: AbstractAccountRepository = SqlAlchemyAccountRepository(
        session
    )
    beneficiary_repository: AbstractBeneficiaryRepository = (
        SqlAlchemyBeneficiaryRepository(session)
    )
    return TransactionService(
        session=session,
        transaction_repository=transaction_repository,
        account_repository=account_repository,
        beneficiary_repository=beneficiary_repository,
    )