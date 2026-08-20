from pydantic import BaseModel,ConfigDict
from datetime import date
from enums import AccountStatus, UserStatus, Role, CardStatus
from decimal import Decimal


class UpdateUserStatusCommand(BaseModel):
    user_id: int
    status: UserStatus
    rejection_reason: str | None = None

class UpdateAccountStatus(BaseModel):
    account_id: int
    account_status: AccountStatus
    close_reason: str | None = None



class UpdateCardStatus(BaseModel):
    card_id: int
    status: CardStatus

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: Role
    dob: date | None = None
    address_line: str | None = None
    city: str | None = None
    postcode: str | None = None
    mobile: str | None = None
    rejection_reason: str | None = None
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)

class AdminUserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: Role
    dob: date | None = None
    address_line: str | None = None
    user_status: UserStatus
    city: str | None = None
    postcode: str | None = None
    mobile: str | None = None
    rejection_reason: str | None = None
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)

class AdminLoanResponse(BaseModel):
    id: int

    loan_type: str
    loan_amount: Decimal
    duration: int
    interest: int | float
    emi: Decimal

    current_loan_status: str

    user_id: int
    first_name: str
    last_name: str
    email: str