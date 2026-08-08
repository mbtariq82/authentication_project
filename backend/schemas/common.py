from pydantic import BaseModel, EmailStr, field_validator


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
