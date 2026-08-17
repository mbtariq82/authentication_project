from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.transaction import Transaction, TransactionLog
from enums import TransactionStatus
from models.account import AccountRow
from models.transaction import TransactionLogRow, TransactionRow
from repositories.abstract_transaction_repository import (
    AbstractTransactionRepository,
)
from schemas.transaction import TransactionFilter


class SqlAlchemyTransactionRepository(AbstractTransactionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_transaction(row: TransactionRow) -> Transaction:
        return Transaction(
            id=row.id,
            account_id=row.account_id,
            beneficiary_id=row.beneficiary_id,
            transaction_type=row.transaction_type,
            direction=row.direction,
            amount=row.amount,
            status=row.status,
            reference=row.reference,
            transfer_reference=row.transfer_reference,
            description=row.description,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    @staticmethod
    def _to_log(row: TransactionLogRow) -> TransactionLog:
        return TransactionLog(
            id=row.id,
            transaction_id=row.transaction_id,
            user_id=row.user_id,
            action=row.action,
            status=row.status,
            message=row.message,
            metadata=row.metadata_json,
            created_at=row.created_at,
        )

    async def add(self, transaction: Transaction) -> Transaction:
        row = TransactionRow(
            account_id=transaction.account_id,
            beneficiary_id=transaction.beneficiary_id,
            transaction_type=transaction.transaction_type,
            direction=transaction.direction,
            amount=transaction.amount,
            status=transaction.status,
            reference=transaction.reference,
            transfer_reference=transaction.transfer_reference,
            description=transaction.description,
        )
        self.session.add(row)
        await self.session.flush()
        await self.session.refresh(row)
        return self._to_transaction(row)

    def _owned_transaction_query(self, user_id: int):
        return (
            select(TransactionRow)
            .join(AccountRow, AccountRow.id == TransactionRow.account_id)
            .where(AccountRow.user_id == user_id)
        )

    async def get_by_id_for_user(
        self,
        transaction_id: int,
        user_id: int,
    ) -> Transaction | None:
        result = await self.session.execute(
            self._owned_transaction_query(user_id).where(
                TransactionRow.id == transaction_id
            )
        )
        row = result.scalar_one_or_none()
        return self._to_transaction(row) if row else None

    async def list_by_user(
        self,
        user_id: int,
        filters: TransactionFilter,
    ) -> tuple[list[Transaction], int]:
        conditions = [AccountRow.user_id == user_id]
        if filters.status is not None:
            conditions.append(TransactionRow.status == filters.status)
        if filters.transaction_type is not None:
            conditions.append(
                TransactionRow.transaction_type == filters.transaction_type
            )
        if filters.direction is not None:
            conditions.append(TransactionRow.direction == filters.direction)
        if filters.reference is not None:
            conditions.append(TransactionRow.reference == filters.reference)
        if filters.created_from is not None:
            conditions.append(TransactionRow.created_at >= filters.created_from)
        if filters.created_to is not None:
            conditions.append(TransactionRow.created_at <= filters.created_to)

        count_result = await self.session.execute(
            select(func.count(TransactionRow.id))
            .select_from(TransactionRow)
            .join(AccountRow, AccountRow.id == TransactionRow.account_id)
            .where(*conditions)
        )
        total = count_result.scalar_one()

        result = await self.session.execute(
            self._owned_transaction_query(user_id)
            .where(*conditions[1:])
            .order_by(TransactionRow.created_at.desc(), TransactionRow.id.desc())
            .offset(filters.offset)
            .limit(filters.limit)
        )
        items = [self._to_transaction(row) for row in result.scalars().all()]
        return items, total

    async def update_status(
        self,
        transaction_id: int,
        user_id: int,
        status: TransactionStatus,
    ) -> Transaction | None:
        result = await self.session.execute(
            self._owned_transaction_query(user_id)
            .where(TransactionRow.id == transaction_id)
            .with_for_update()
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        row.status = status
        await self.session.flush()
        await self.session.refresh(row)
        return self._to_transaction(row)

    async def add_log(self, log: TransactionLog) -> TransactionLog:
        row = TransactionLogRow(
            transaction_id=log.transaction_id,
            user_id=log.user_id,
            action=log.action,
            status=log.status,
            message=log.message,
            metadata_json=log.metadata,
        )
        self.session.add(row)
        await self.session.flush()
        await self.session.refresh(row)
        return self._to_log(row)

    async def list_logs(
        self,
        transaction_id: int,
        user_id: int,
    ) -> list[TransactionLog]:
        result = await self.session.execute(
            select(TransactionLogRow)
            .join(
                TransactionRow,
                TransactionRow.id == TransactionLogRow.transaction_id,
            )
            .join(AccountRow, AccountRow.id == TransactionRow.account_id)
            .where(
                TransactionLogRow.transaction_id == transaction_id,
                AccountRow.user_id == user_id,
            )
            .order_by(TransactionLogRow.created_at.asc(), TransactionLogRow.id.asc())
        )
        return [self._to_log(row) for row in result.scalars().all()]