from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer

class CardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    card_number: str
    cvc: str
    expiry_date: datetime
    status: str
    created_at: datetime

class CardDetailsRequest(BaseModel):
    password: str

class CardDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    card_number: str
    expiry_date: datetime
    cvc: str

    @field_serializer("expiry_date")
    def serialize_expiry_date(self, value: datetime) -> str:
        return value.strftime("%m/%y")