from pydantic import BaseModel,ConfigDict
from datetime import date
from enums import UserStatus, Role


class UserStatusUpdate(BaseModel):
    status: UserStatus

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: Role
    dob: date
    address_line: str
    city: str
    county: str
    postcode: str
    mobile: str | None = None
    rejection_reason: str | None = None
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)