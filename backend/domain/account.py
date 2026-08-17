from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(slots=True)
class Account:
    user_id: int
    balance: Decimal = Decimal("0.00")
    id: int | None = None
    sort_code: str | None = None
    branch: str | None = None
    account_type: str | None = None
    account_number: str | None = None
    account_status: str | None = None
    is_deleted: bool = False
    close_reason: str | None = None
    closed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None