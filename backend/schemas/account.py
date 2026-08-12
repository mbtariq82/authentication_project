from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    loan_id: int | None = None
    document_id: int | None = None
    sort_code: str | None = None
    account_number: str | None = None
    balance: Decimal
    account_status: str | None = None
    opened_at: datetime | None = None
    closed_at: datetime | None = None
