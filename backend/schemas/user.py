from datetime import date

from pydantic import BaseModel, ConfigDict

from enums import Role


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str
    last_name: str
    role: Role
    profile_image_url: str | None = None
    phone: str | None = None
    address: str | None = None
    dob: date | None = None
    postcode: str | None = None
    country: str | None = None
    city: str | None = None


class UpdateUserProfileCommand(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    profile_image: bytes | None = None
