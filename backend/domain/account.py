from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(slots=True)
class Account:
    user_id: int
    balance: Decimal = Decimal("0.00")
    id: int | None = None
    created_at: datetime | None = None
