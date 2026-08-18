from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from enums import TransactionDirection, TransactionStatus, TransactionType
from exceptions import (
    InvalidTransactionRuleError,
    InvalidTransactionStatusTransitionError,
)


class TransferKind(StrEnum):
    INTERNAL = "INTERNAL"
    UK_LOCAL = "UK_LOCAL"


@dataclass(frozen=True, slots=True)
class BalanceEffect:
    credit: Decimal = Decimal("0.00")
    debit: Decimal = Decimal("0.00")


ALLOWED_STATUS_TRANSITIONS: dict[
    TransactionStatus, frozenset[TransactionStatus]
] = {
    TransactionStatus.PENDING: frozenset(
        {
            TransactionStatus.COMPLETED,
            TransactionStatus.FAILED,
            TransactionStatus.CANCELLED,
        }
    ),
    TransactionStatus.COMPLETED: frozenset(),
    TransactionStatus.FAILED: frozenset(),
    TransactionStatus.CANCELLED: frozenset(),
}


def validate_transaction_shape(
    transaction_type: TransactionType,
    direction: TransactionDirection,
    beneficiary_id: int | None,
) -> None:
    expected_direction = expected_direction_for(transaction_type)
    if direction != expected_direction:
        raise InvalidTransactionRuleError(
            f"{transaction_type} transactions must have "
            f"{expected_direction} direction"
        )
    if transaction_type is TransactionType.TRANSFER and beneficiary_id is None:
        raise InvalidTransactionRuleError(
            "TRANSFER transactions require a beneficiary"
        )
    if transaction_type is not TransactionType.TRANSFER and beneficiary_id is not None:
        raise InvalidTransactionRuleError(
            "Only TRANSFER transactions may specify a beneficiary"
        )


def expected_direction_for(
    transaction_type: TransactionType,
) -> TransactionDirection:
    return {
        TransactionType.DEPOSIT: TransactionDirection.CREDIT,
        TransactionType.WITHDRAWAL: TransactionDirection.DEBIT,
        TransactionType.TRANSFER: TransactionDirection.DEBIT,
    }[transaction_type]


def validate_status_transition(
    current: TransactionStatus,
    requested: TransactionStatus,
) -> None:
    if requested not in ALLOWED_STATUS_TRANSITIONS[current]:
        raise InvalidTransactionStatusTransitionError(
            f"Cannot transition transaction from {current} to {requested}"
        )


def balance_effect(
    transaction_type: TransactionType,
    direction: TransactionDirection,
    amount: Decimal,
    status: TransactionStatus,
) -> BalanceEffect:
    if amount <= 0:
        raise InvalidTransactionRuleError("Transaction amount must be positive")
    if direction != expected_direction_for(transaction_type):
        raise InvalidTransactionRuleError(
            f"{transaction_type} transactions must have "
            f"{expected_direction_for(transaction_type)} direction"
        )
    if status is not TransactionStatus.COMPLETED:
        return BalanceEffect()
    if direction is TransactionDirection.CREDIT:
        return BalanceEffect(credit=amount)
    return BalanceEffect(debit=amount)


def classify_transfer(
    beneficiary_account_number: str,
    account_numbers: set[str],
) -> TransferKind:
    if beneficiary_account_number in account_numbers:
        return TransferKind.INTERNAL
    return TransferKind.UK_LOCAL