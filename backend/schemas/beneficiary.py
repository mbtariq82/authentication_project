from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BeneficiaryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    account_number: str = Field(min_length=1, max_length=50)
    sort_code: str = Field(min_length=1, max_length=20)
    bank_name: str = Field(min_length=1, max_length=150)
    reference: str | None = Field(default=None, max_length=255)

    @field_validator("name", "account_number", "sort_code", "bank_name", mode="before")
    @classmethod
    def strip_required_text(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
        return value

    @field_validator("reference", mode="before")
    @classmethod
    def normalize_reference(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class BeneficiaryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    account_number: str | None = Field(default=None, min_length=1, max_length=50)
    sort_code: str | None = Field(default=None, min_length=1, max_length=20)
    bank_name: str | None = Field(default=None, min_length=1, max_length=150)
    reference: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None

    @field_validator(
        "name", "account_number", "sort_code", "bank_name", "reference", mode="before"
    )
    @classmethod
    def strip_optional_text(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value


class BeneficiaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    account_number: str
    sort_code: str
    bank_name: str
    reference: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
