from pydantic import BaseModel,ConfigDict
from datetime import date
from enums import UserStatus, Role


class UpdateUserStatusCommand(BaseModel):
    user_id: int
    status: UserStatus
    rejection_reason: str | None = None

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
