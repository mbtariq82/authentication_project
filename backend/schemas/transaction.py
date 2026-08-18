from datetime import datetime
from decimal import Decimal
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_validator

from enums import TransactionDirection, TransactionStatus, TransactionType


class TransactionCreate(BaseModel):
    account_id: int = Field(gt=0)
    beneficiary_id: int | None = Field(default=None, gt=0)
    transaction_type: TransactionType
    direction: TransactionDirection
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    transfer_reference: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_transaction_shape(self) -> "TransactionCreate":
        expected_direction = {
            TransactionType.DEPOSIT: TransactionDirection.CREDIT,
            TransactionType.WITHDRAWAL: TransactionDirection.DEBIT,
            TransactionType.TRANSFER: TransactionDirection.DEBIT,
        }[self.transaction_type]
        if self.direction != expected_direction:
            raise ValueError(
                f"{self.transaction_type} transactions must have "
                f"{expected_direction} direction"
            )
        if self.transaction_type is TransactionType.TRANSFER:
            if self.beneficiary_id is None:
                raise ValueError("TRANSFER transactions require a beneficiary")
        elif self.beneficiary_id is not None:
            raise ValueError(
                "Only TRANSFER transactions may specify a beneficiary"
            )
        return self


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    beneficiary_id: int | None = None
    transaction_type: TransactionType
    direction: TransactionDirection
    amount: Decimal
    status: TransactionStatus
    reference: str
    transfer_reference: str | None = None
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class TransactionFilter(BaseModel):
    status: TransactionStatus | None = None
    transaction_type: TransactionType | None = None
    direction: TransactionDirection | None = None
    reference: str | None = Field(default=None, max_length=100)
    created_from: datetime | None = None
    created_to: datetime | None = None
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=100)

    @model_validator(mode="after")
    def validate_date_range(self) -> "TransactionFilter":
        if (
            self.created_from is not None
            and self.created_to is not None
            and self.created_from > self.created_to
        ):
            raise ValueError("created_from must be before created_to")
        return self


class TransactionLogResponse(BaseModel):
    id: int
    transaction_id: int
    user_id: int | None = None
    action: str
    status: str
    message: str | None = None
    metadata: dict[str, Any] | None = None
    created_at: datetime


ResponseItem = TypeVar("ResponseItem")


class PaginatedResponse(BaseModel, Generic[ResponseItem]):
    items: list[ResponseItem]
    offset: int
    limit: int
    total: int
