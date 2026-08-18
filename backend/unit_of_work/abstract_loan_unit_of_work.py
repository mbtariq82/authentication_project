
from abc import ABC, abstractmethod

from repositories.sqlalchemy_loan_repository import SQLAlchemyLoanRepository


class AbstractLoanUnitOfWork(ABC):

    loans: SQLAlchemyLoanRepository

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