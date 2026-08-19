from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    sort_code: str | None = None
    branch: str | None = None
    account_type: str | None = None
    account_number: str | None = None
    balance: Decimal
    account_status: str | None = None
    is_deleted: bool = False
    close_reason: str | None = None
    closed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AdminAccountResponse(BaseModel):
    id: int
    user_id: int

    sort_code: str | None
    branch: str | None
    account_type: str
    account_number: str | None
    balance: str | float | int
    account_status: str
    is_deleted: bool
    close_reason: str | None = None
    closed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    first_name: str
    last_name: str
    email: str

    model_config = ConfigDict(from_attributes=True)