from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(slots=True)
class Account:
    user_id: int
    balance: Decimal = Decimal("0.00")
    id: int | None = None
    document_id: int | None = None
    sort_code: str | None = None
    account_number: str | None = None
    account_status: str | None = None
    opened_at: datetime | None = None
    closed_at: datetime | None = None
