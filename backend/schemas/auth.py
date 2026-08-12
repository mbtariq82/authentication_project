from pydantic import BaseModel

from schemas.common import EmailCommand


class RegisterCommand(EmailCommand):
    first_name: str
    last_name: str
    password: str


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
