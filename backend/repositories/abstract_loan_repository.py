from abc import ABC, abstractmethod
from typing import Optional, List
from models.loan import LoanRow


class AbstractLoanRepository(ABC):

    @abstractmethod
    async def create(self, loan: LoanRow) -> LoanRow:
        raise NotImplementedError

    @abstractmethod
    async def get_pending_loans(self) -> list[LoanRow]:
        not NotImplementedError

    @abstractmethod
    async def get_loan_by_id(self, loan_id: int) -> Optional[LoanRow]:
        raise NotImplementedError

    @abstractmethod
    async def get_loans_by_account_id(self, account_id: int) -> List[LoanRow]:
        raise NotImplementedError