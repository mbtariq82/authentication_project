from datetime import datetime, timezone
from enum import StrEnum
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RegistrationMethod(StrEnum):
    PASSWORD = "password"
    GOOGLE = "google"


class UserRegisteredDataV1(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_id: int = Field(gt=0)
    registration_method: RegistrationMethod


class UserRegisteredV1(BaseModel):
    model_config = ConfigDict(frozen=True)

    event_id: UUID = Field(default_factory=uuid4)
    event_type: Literal["identity.user_registered"] = (
        "identity.user_registered"
    )
    schema_version: Literal[1] = 1
    producer: Literal["authentication-service"] = "authentication-service"
    occurred_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    correlation_id: UUID
    data: UserRegisteredDataV1

    @field_validator("occurred_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("occurred_at must be timezone-aware")

        return value.astimezone(timezone.utc)