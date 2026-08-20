from abc import ABC, abstractmethod
from decimal import Decimal

from domain.account import Account


class AbstractAccountRepository(ABC):
    @abstractmethod
    async def add(self, account: Account) -> Account:
        raise NotImplementedError

    @abstractmethod
    async def get_by_user(self, user_id: int) -> Account | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id_for_user(
        self,
        account_id: int,
        user_id: int,
    ) -> Account | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_account_number_and_sort_code(
        self,
        account_number: str,
        sort_code: str,
    ) -> Account | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id_for_update(self, account_id: int) -> Account | None:
        raise NotImplementedError

    @abstractmethod
    async def close(self, account_id: int, close_reason: str) -> Account:
        raise NotImplementedError

    @abstractmethod
    async def credit(self, account_id: int, amount: Decimal) -> Account:
        raise NotImplementedError

    @abstractmethod
    async def debit(self, account_id: int, amount: Decimal) -> Account:
        raise NotImplementedError

    @abstractmethod
    async def set_status( self, account_id: int, account_status: str) -> Account:
        raise NotImplementedError
