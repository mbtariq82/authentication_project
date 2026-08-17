from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from domain.transaction import Transaction, TransactionLog
from domain.transaction_rules import (
    balance_effect,
    validate_status_transition,
)
from enums import TransactionStatus, TransactionType
from exceptions import (
    BeneficiaryNotFoundError,
    InvalidTransactionStatusTransitionError,
    TransactionNotFoundError,
)
from repositories.abstract_account_repository import AbstractAccountRepository
from repositories.abstract_beneficiary_repository import (
    AbstractBeneficiaryRepository,
)
from repositories.abstract_transaction_repository import (
    AbstractTransactionRepository,
)
from schemas.transaction import (
    PaginatedResponse,
    TransactionCreate,
    TransactionFilter,
    TransactionLogResponse,
    TransactionResponse,
)


class TransactionService:
    def __init__(
        self,
        session: AsyncSession,
        transaction_repository: AbstractTransactionRepository,
        account_repository: AbstractAccountRepository,
        beneficiary_repository: AbstractBeneficiaryRepository,
    ):
        self.session = session
        self.transactions = transaction_repository
        self.accounts = account_repository
        self.beneficiaries = beneficiary_repository

    async def create(
        self,
        user_id: int,
        command: TransactionCreate,
    ) -> TransactionResponse:
        account = await self.accounts.get_by_id_for_user(
            command.account_id,
            user_id,
        )
        if account is None:
            raise TransactionNotFoundError()

        if command.transaction_type is TransactionType.TRANSFER:
            beneficiary = await self.beneficiaries.get_by_id(
                command.beneficiary_id,
                user_id,
            )
            if beneficiary is None or not beneficiary.is_active:
                raise BeneficiaryNotFoundError()

        status = (
            TransactionStatus.COMPLETED
            if command.transaction_type in {
                TransactionType.DEPOSIT,
                TransactionType.WITHDRAWAL,
            }
            else TransactionStatus.PENDING
        )
        transaction = await self.transactions.add(
            Transaction(
                account_id=command.account_id,
                beneficiary_id=command.beneficiary_id,
                transaction_type=command.transaction_type,
                direction=command.direction,
                amount=command.amount,
                status=status,
                reference=self._new_reference(),
                transfer_reference=command.transfer_reference,
                description=command.description,
            )
        )

        effect = balance_effect(
            transaction.transaction_type,
            transaction.direction,
            transaction.amount,
            transaction.status,
        )
        if effect.credit:
            await self.accounts.credit(transaction.account_id, effect.credit)
        if effect.debit:
            await self.accounts.debit(transaction.account_id, effect.debit)

        await self.transactions.add_log(
            TransactionLog(
                transaction_id=transaction.id,
                user_id=user_id,
                action="CREATE",
                status=transaction.status.value,
                message="Transaction created",
            )
        )
        await self.session.commit()
        return transaction_response(transaction)

    async def list_transactions(
        self,
        user_id: int,
        filters: TransactionFilter,
    ) -> PaginatedResponse[TransactionResponse]:
        items, total = await self.transactions.list_by_user(user_id, filters)
        return PaginatedResponse(
            items=[transaction_response(item) for item in items],
            offset=filters.offset,
            limit=filters.limit,
            total=total,
        )

    async def get(
        self,
        user_id: int,
        transaction_id: int,
    ) -> TransactionResponse:
        transaction = await self.transactions.get_by_id_for_user(
            transaction_id,
            user_id,
        )
        if transaction is None:
            raise TransactionNotFoundError()
        return transaction_response(transaction)

    async def cancel(
        self,
        user_id: int,
        transaction_id: int,
    ) -> TransactionResponse:
        transaction = await self.transactions.get_by_id_for_user(
            transaction_id,
            user_id,
        )
        if transaction is None:
            raise TransactionNotFoundError()
        validate_status_transition(transaction.status, TransactionStatus.CANCELLED)
        cancelled = await self.transactions.update_status(
            transaction_id,
            user_id,
            TransactionStatus.CANCELLED,
        )
        if cancelled is None:
            raise TransactionNotFoundError()
        await self.transactions.add_log(
            TransactionLog(
                transaction_id=transaction_id,
                user_id=user_id,
                action="CANCEL",
                status=TransactionStatus.CANCELLED.value,
                message="Transaction cancelled",
            )
        )
        await self.session.commit()
        return transaction_response(cancelled)

    async def logs(
        self,
        user_id: int,
        transaction_id: int,
        *,
        is_admin: bool = False,
    ) -> list[TransactionLogResponse]:
        transaction = await (
            self.transactions.get_by_id_for_admin(transaction_id)
            if is_admin
            else self.transactions.get_by_id_for_user(transaction_id, user_id)
        )
        if is_admin:
            entries = await self.transactions.list_logs_for_admin(transaction_id)
        else:
            entries = await self.transactions.list_logs(transaction_id, user_id)
        if transaction is None:
            raise TransactionNotFoundError()
        return [
            TransactionLogResponse(
                id=entry.id,
                transaction_id=entry.transaction_id,
                user_id=entry.user_id,
                action=entry.action,
                status=entry.status,
                message=entry.message,
                metadata=entry.metadata,
                created_at=entry.created_at,
            )
            for entry in entries
        ]

    @staticmethod
    def _new_reference() -> str:
        return uuid4().hex


def transaction_response(transaction: Transaction) -> TransactionResponse:
    return TransactionResponse(
        id=transaction.id,
        account_id=transaction.account_id,
        beneficiary_id=transaction.beneficiary_id,
        transaction_type=transaction.transaction_type,
        direction=transaction.direction,
        amount=transaction.amount,
        status=transaction.status,
        reference=transaction.reference,
        transfer_reference=transaction.transfer_reference,
        description=transaction.description,
        created_at=transaction.created_at,
        updated_at=transaction.updated_at,
    )