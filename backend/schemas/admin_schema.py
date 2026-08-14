from pydantic import BaseModel,ConfigDict
from datetime import date
from enums import UserStatus, Role


class UserStatusUpdate(BaseModel):
    user_status: UserStatus

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: Role
    dob: date | None = None
    address_line: str | None = None
    city: str | None = None
    county: str | None = None
    postcode: str | None = None
    mobile: str | None = None
    rejection_reason: str | None = None
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)
