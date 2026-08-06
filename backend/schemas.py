from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from enums import Role

ALLOWED_EMAIL_DOMAIN = "@informationtechconsultants.co.uk"
class EmailCommand(BaseModel):
    email: EmailStr
    @field_validator("email")
    @classmethod
    def validate_email_domain(cls, email: str) -> str:
        normalized_email = email.lower()
        if not normalized_email.endswith(ALLOWED_EMAIL_DOMAIN):
            raise ValueError(
                "Email must end with @informationtechconsultants.co.uk"
            )
        return normalized_email

class RegisterCommand(EmailCommand):
    first_name: str
    last_name: str
    password: str
    #full_name
    #mfa

class LoginCommand(EmailCommand):
    password: str
    #captcha
    #mfa

class GoogleLoginCommand(BaseModel):
    id_token: str
    #device_id
    #referrel_code
    #remember_me

# response type from Google
class GoogleIdentity(BaseModel):    # email validation will not work here
    subject: str
    email: str
    email_verified: bool

class LogoutCommand(BaseModel):
    token: str
    #session_id

class RefreshCommand(BaseModel):
    token: str
    #session_id

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# Public representation of a User returned by the API.
# Keeping this separate from the SQLAlchemy User model prevents exposing
# internal fields (e.g. hashed_password) and decouples the API contract
# from the database schema.
# better name would be PublicUserDetails
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    first_name: str
    last_name: str
    role: Role
    #full_name