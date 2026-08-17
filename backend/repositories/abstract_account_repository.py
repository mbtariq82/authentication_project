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
    async def get_by_id_for_update(self, account_id: int) -> Account | None:
        raise NotImplementedError

    @abstractmethod
    async def credit(self, account_id: int, amount: Decimal) -> Account:
        raise NotImplementedError

    @abstractmethod
    async def debit(self, account_id: int, amount: Decimal) -> Account:
        raise NotImplementedError
