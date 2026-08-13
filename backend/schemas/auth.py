from pydantic import BaseModel, Field, field_validator

from schemas.common import EmailCommand


class RegisterCommand(EmailCommand):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=12, max_length=72)

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def normalize_name(cls, name: object) -> object:
        if isinstance(name, str):
            return name.strip()
        return name

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, password: str) -> str:
        requirements = (
            any(character.islower() for character in password),
            any(character.isupper() for character in password),
            any(character.isdigit() for character in password),
            any(
                not character.isalnum() and not character.isspace()
                for character in password
            ),
        )
        if not all(requirements):
            raise ValueError(
                "Password must contain uppercase, lowercase, number, and "
                "special characters"
            )
        return password


class LoginCommand(EmailCommand):
    password: str


class GoogleLoginCommand(BaseModel):
    id_token: str


class GoogleIdentity(BaseModel):
    subject: str
    email: str
    email_verified: bool
    first_name: str | None = None
    last_name: str | None = None


class LogoutCommand(BaseModel):
    token: str


class RefreshCommand(BaseModel):
    token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
