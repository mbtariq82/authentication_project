from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Beneficiary:
    user_id: int
    name: str
    account_number: str
    sort_code: str
    bank_name: str
    reference: str | None = None
    is_active: bool = True
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
