from abc import ABC, abstractmethod

from domain.transaction import Transaction, TransactionLog
from enums import TransactionStatus
from schemas.transaction import TransactionFilter


class AbstractTransactionRepository(ABC):
    @abstractmethod
    async def add(self, transaction: Transaction) -> Transaction:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id_for_user(
        self,
        transaction_id: int,
        user_id: int,
    ) -> Transaction | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id_for_admin(
        self,
        transaction_id: int,
    ) -> Transaction | None:
        raise NotImplementedError

    @abstractmethod
    async def list_by_user(
        self,
        user_id: int,
        filters: TransactionFilter,
    ) -> tuple[list[Transaction], int]:
        raise NotImplementedError

    @abstractmethod
    async def update_status(
        self,
        transaction_id: int,
        user_id: int,
        status: TransactionStatus,
    ) -> Transaction | None:
        raise NotImplementedError

    @abstractmethod
    async def add_log(self, log: TransactionLog) -> TransactionLog:
        raise NotImplementedError

    @abstractmethod
    async def list_logs(
        self,
        transaction_id: int,
        user_id: int,
    ) -> list[TransactionLog]:
        raise NotImplementedError

    @abstractmethod
    async def list_logs_for_admin(
        self,
        transaction_id: int,
    ) -> list[TransactionLog]:
        raise NotImplementedError
