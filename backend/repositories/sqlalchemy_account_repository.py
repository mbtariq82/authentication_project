from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.account import Account
from datetime import datetime, timezone

from exceptions import (
    AccountAlreadyClosedError,
    AccountBalanceNotZeroError,
    AccountNotFoundError,
    InsufficientFundsError,
    InvalidBalanceAmountError,
)
from enums import AccountStatus
from models.account import AccountRow
from repositories.abstract_account_repository import AbstractAccountRepository


class SqlAlchemyAccountRepository(AbstractAccountRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_domain(row: AccountRow) -> Account:
        return Account(
            id=row.id,
            user_id=row.user_id,
            sort_code=row.sort_code,
            branch=row.branch,
            account_type=row.account_type,
            account_number=row.account_number,
            balance=row.balance,
            account_status=row.account_status,
            is_deleted=row.is_deleted,
            close_reason=row.close_reason,
            closed_at=row.closed_at,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    async def add(self, account: Account) -> Account:
        row = AccountRow(
            user_id=account.user_id,
            sort_code=account.sort_code,
            account_number=account.account_number,
            balance=account.balance,
            account_status=account.account_status,
            closed_at=account.closed_at,
        )
        self.session.add(row)
        await self.session.flush()
        await self.session.refresh(row)
        return self._to_domain(row)

    async def get_by_user(self, user_id: int) -> Account | None:
        result = await self.session.execute(
            select(AccountRow).where(AccountRow.user_id == user_id)
        )
        row = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def get_by_id_for_user(
        self,
        account_id: int,
        user_id: int,
    ) -> Account | None:
        result = await self.session.execute(
            select(AccountRow).where(
                AccountRow.id == account_id,
                AccountRow.user_id == user_id,
            )
        )
        row = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def get_by_id_for_update(self, account_id: int) -> Account | None:
        result = await self.session.execute(
            select(AccountRow)
            .where(AccountRow.id == account_id)
            .with_for_update()
        )
        row = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def credit(self, account_id: int, amount: Decimal) -> Account:
        if amount <= 0:
            raise InvalidBalanceAmountError()

        result = await self.session.execute(
            select(AccountRow)
            .where(AccountRow.id == account_id)
            .with_for_update()
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise AccountNotFoundError()

        row.balance += amount
        await self.session.flush()
        await self.session.refresh(row)
        return self._to_domain(row)

    async def debit(self, account_id: int, amount: Decimal) -> Account:
        if amount <= 0:
            raise InvalidBalanceAmountError()

        result = await self.session.execute(
            select(AccountRow)
            .where(AccountRow.id == account_id)
            .with_for_update()
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise AccountNotFoundError()
        if row.balance < amount:
            raise InsufficientFundsError()

        row.balance -= amount
        await self.session.flush()
        await self.session.refresh(row)
        return self._to_domain(row)

    async def close(self, account_id: int, close_reason: str) -> Account:
        result = await self.session.execute(
            select(AccountRow)
            .where(AccountRow.id == account_id)
            .with_for_update()
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise AccountNotFoundError()

        row.is_deleted = True
        row.account_status = AccountStatus.CLOSED.value
        row.close_reason = close_reason
        row.closed_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(row)
        return self._to_domain(row)
