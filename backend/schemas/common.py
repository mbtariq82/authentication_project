from pydantic import BaseModel, EmailStr, field_validator


class EmailCommand(BaseModel):
    email: EmailStr

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, email: object) -> object:
        if isinstance(email, str):
            return email.strip().lower()
        return email
