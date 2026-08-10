from abc import ABC, abstractmethod

from domain.account import Account


class AbstractAccountRepository(ABC):
    @abstractmethod
    async def add(self, account: Account) -> Account:
        raise NotImplementedError

    @abstractmethod
    async def get_by_user(self, user_id: int) -> Account | None:
        raise NotImplementedError
