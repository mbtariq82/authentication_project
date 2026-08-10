from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from enums import AccountStatus, ApprovalStatus


class CreateAccountCommand(BaseModel):
    account_type_id: int


class RejectAccountCommand(BaseModel):
    reason: str = Field(min_length=1, max_length=500)


class AccountTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    interest_rate: Decimal
    minimum_balance: Decimal
    allows_overdraft: bool


class BalanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: int
    ledger_balance: Decimal
    available_balance: Decimal
    updated_at: datetime | None = None


class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    account_type_id: int
    account_number: str | None
    admin_approved: ApprovalStatus
    status: AccountStatus
    created_at: datetime | None = None