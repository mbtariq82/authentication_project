from datetime import datetime, timezone
from decimal import Decimal

import pytest

from domain.account import Account
from domain.beneficiary import Beneficiary
from domain.transaction import Transaction, TransactionLog
from enums import TransactionDirection, TransactionStatus, TransactionType
from exceptions import (
    InsufficientFundsError,
    InvalidTransactionStatusTransitionError,
)
from schemas.transaction import TransactionCreate, TransactionFilter
from services.transaction_service import TransactionService


class FakeTransactionUnitOfWork:
    def __init__(self, account: Account):
        self.accounts = FakeAccountRepository(account)
        self.beneficiaries = FakeBeneficiaryRepository()
        self.transactions = FakeTransactionRepository()
        self.commits = 0

    async def commit(self) -> None:
        self.commits += 1


class FakeAccountRepository:
    def __init__(self, account: Account):
        self.account = account
        self.internal_account: Account | None = None
        self.recipient_lookups: list[tuple[str, str]] = []
        self.credited: list[Decimal] = []
        self.debited: list[Decimal] = []

    async def get_by_id_for_user(self, account_id: int, user_id: int):
        if self.account.id == account_id and self.account.user_id == user_id:
            return self.account
        return None

    async def get_by_account_number_and_sort_code(
        self,
        account_number: str,
        sort_code: str,
    ):
        self.recipient_lookups.append((account_number, sort_code))
        return self.internal_account

    async def credit(self, account_id: int, amount: Decimal):
        self.credited.append(amount)
        return self.account

    async def debit(self, account_id: int, amount: Decimal):
        if self.account.balance < amount:
            raise InsufficientFundsError()
        self.debited.append(amount)
        return self.account


class FakeBeneficiaryRepository:
    def __init__(self):
        self.beneficiary = Beneficiary(
            id=2,
            user_id=1,
            name="Recipient",
            account_number="12345678",
            sort_code="010203",
            bank_name="Test Bank",
        )

    async def get_by_id(self, beneficiary_id: int, user_id: int):
        if beneficiary_id == self.beneficiary.id and user_id == self.beneficiary.user_id:
            return self.beneficiary
        return None


class FakeTransactionRepository:
    def __init__(self):
        self.items: list[Transaction] = []
        self.logs: list[TransactionLog] = []
        self.next_id = 1

    async def add(self, transaction: Transaction):
        transaction.id = self.next_id
        self.next_id += 1
        now = datetime.now(timezone.utc)
        transaction.created_at = now
        transaction.updated_at = now
        self.items.append(transaction)
        return transaction

    async def get_by_id_for_user(self, transaction_id: int, user_id: int):
        return next((item for item in self.items if item.id == transaction_id), None)

    async def get_by_id_for_admin(self, transaction_id: int):
        return next((item for item in self.items if item.id == transaction_id), None)

    async def list_by_user(self, user_id: int, filters: TransactionFilter):
        return self.items, len(self.items)

    async def update_status(self, transaction_id: int, user_id: int, status):
        item = await self.get_by_id_for_user(transaction_id, user_id)
        if item:
            item.status = status
        return item

    async def add_log(self, log: TransactionLog):
        log.id = len(self.logs) + 1
        log.created_at = datetime.now(timezone.utc)
        self.logs.append(log)
        return log

    async def list_logs(self, transaction_id: int, user_id: int):
        return [log for log in self.logs if log.transaction_id == transaction_id]

    async def list_logs_for_admin(self, transaction_id: int):
        return [log for log in self.logs if log.transaction_id == transaction_id]


@pytest.fixture
def service_and_uow():
    account = Account(user_id=1, id=1, balance=Decimal("100.00"))
    unit_of_work = FakeTransactionUnitOfWork(account)
    return TransactionService(unit_of_work), unit_of_work


@pytest.mark.asyncio
async def test_create_completed_deposit_updates_balance(service_and_uow):
    service, unit_of_work = service_and_uow
    response = await service.create(
        1,
        TransactionCreate(
            account_id=1,
            transaction_type=TransactionType.DEPOSIT,
            direction=TransactionDirection.CREDIT,
            amount=Decimal("25.00"),
        ),
    )

    assert response.status is TransactionStatus.COMPLETED
    assert unit_of_work.accounts.credited == [Decimal("25.00")]
    assert unit_of_work.transactions.logs[0].action == "CREATE"
    assert unit_of_work.commits == 1


@pytest.mark.asyncio
async def test_create_transfer_stays_pending_without_balance_change(service_and_uow):
    service, unit_of_work = service_and_uow
    response = await service.create(
        1,
        TransactionCreate(
            account_id=1,
            beneficiary_id=2,
            transaction_type=TransactionType.TRANSFER,
            direction=TransactionDirection.DEBIT,
            amount=Decimal("25.00"),
        ),
    )

    assert response.status is TransactionStatus.PENDING
    assert unit_of_work.accounts.credited == []
    assert unit_of_work.accounts.debited == []
    assert unit_of_work.accounts.recipient_lookups == [("12345678", "010203")]
    assert unit_of_work.transactions.logs[0].metadata == {
        "transfer_kind": "UK_LOCAL"
    }


@pytest.mark.asyncio
async def test_create_transfer_classifies_matching_account_as_internal(service_and_uow):
    service, unit_of_work = service_and_uow
    unit_of_work.accounts.internal_account = Account(
        user_id=2,
        id=2,
        account_number="12345678",
        sort_code="010203",
    )

    response = await service.create(
        1,
        TransactionCreate(
            account_id=1,
            beneficiary_id=2,
            transaction_type=TransactionType.TRANSFER,
            direction=TransactionDirection.DEBIT,
            amount=Decimal("25.00"),
        ),
    )

    assert response.status is TransactionStatus.PENDING
    assert unit_of_work.transactions.logs[0].metadata == {
        "transfer_kind": "INTERNAL"
    }
    assert unit_of_work.accounts.credited == []
    assert unit_of_work.accounts.debited == []


@pytest.mark.asyncio
async def test_cancel_completed_transaction_is_rejected(service_and_uow):
    service, _ = service_and_uow
    response = await service.create(
        1,
        TransactionCreate(
            account_id=1,
            transaction_type=TransactionType.DEPOSIT,
            direction=TransactionDirection.CREDIT,
            amount=Decimal("25.00"),
        ),
    )

    with pytest.raises(InvalidTransactionStatusTransitionError):
        await service.cancel(1, response.id)
