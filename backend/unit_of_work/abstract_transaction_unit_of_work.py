from abc import ABC, abstractmethod
from typing import Self

from repositories.abstract_account_repository import AbstractAccountRepository
from repositories.abstract_beneficiary_repository import (
    AbstractBeneficiaryRepository,
)
from repositories.abstract_transaction_repository import (
    AbstractTransactionRepository,
)


class AbstractTransactionUnitOfWork(ABC):
    accounts: AbstractAccountRepository
    beneficiaries: AbstractBeneficiaryRepository
    transactions: AbstractTransactionRepository

    @abstractmethod
    async def __aenter__(self) -> Self:
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError