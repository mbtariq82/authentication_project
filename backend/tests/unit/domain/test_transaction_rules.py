from decimal import Decimal

import pytest

from domain.transaction_rules import (
    TransferKind,
    balance_effect,
    classify_transfer,
    validate_status_transition,
    validate_transaction_shape,
)
from enums import TransactionDirection, TransactionStatus, TransactionType
from exceptions import (
    InvalidTransactionRuleError,
    InvalidTransactionStatusTransitionError,
)


def test_completed_deposit_credits_balance():
    effect = balance_effect(
        TransactionType.DEPOSIT,
        TransactionDirection.CREDIT,
        Decimal("25.50"),
        TransactionStatus.COMPLETED,
    )

    assert effect.credit == Decimal("25.50")
    assert effect.debit == Decimal("0.00")


def test_pending_withdrawal_has_no_balance_effect():
    effect = balance_effect(
        TransactionType.WITHDRAWAL,
        TransactionDirection.DEBIT,
        Decimal("25.50"),
        TransactionStatus.PENDING,
    )

    assert effect.credit == Decimal("0.00")
    assert effect.debit == Decimal("0.00")


def test_transfer_requires_beneficiary():
    with pytest.raises(InvalidTransactionRuleError):
        validate_transaction_shape(
            TransactionType.TRANSFER,
            TransactionDirection.DEBIT,
            None,
        )


def test_only_pending_transactions_can_transition():
    validate_status_transition(
        TransactionStatus.PENDING,
        TransactionStatus.COMPLETED,
    )

    with pytest.raises(InvalidTransactionStatusTransitionError):
        validate_status_transition(
            TransactionStatus.COMPLETED,
            TransactionStatus.CANCELLED,
        )


def test_transfer_is_classified_by_beneficiary_account_number():
    assert classify_transfer("12345678", {"12345678"}) is TransferKind.INTERNAL
    assert classify_transfer("87654321", {"12345678"}) is TransferKind.UK_LOCAL
