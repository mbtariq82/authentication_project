from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

from enums import TransactionDirection, TransactionStatus, TransactionType


@dataclass(slots=True)
class Transaction:
    account_id: int
    transaction_type: TransactionType
    direction: TransactionDirection
    amount: Decimal
    reference: str
    beneficiary_id: int | None = None
    status: TransactionStatus = TransactionStatus.PENDING
    transfer_reference: str | None = None
    description: str | None = None
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(slots=True)
class TransactionLog:
    transaction_id: int
    action: str
    status: str
    user_id: int | None = None
    message: str | None = None
    metadata: dict[str, Any] | None = None
    id: int | None = None
    created_at: datetime | None = None
