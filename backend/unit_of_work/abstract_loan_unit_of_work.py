from abc import ABC, abstractmethod

from repositories.abstract_loan_repository import AbstractLoanRepository
from repositories.abstract_account_repository import AbstractAccountRepository
from repositories.abstract_transaction_repository import AbstractTransactionRepository

class AbstractLoanUnitOfWork(ABC):

    loans: AbstractLoanRepository
    account: AbstractAccountRepository
    transaction: AbstractTransactionRepository

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback):
        pass

    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass