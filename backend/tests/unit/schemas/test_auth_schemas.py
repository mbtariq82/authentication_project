import pytest
from pydantic import ValidationError

from schemas.auth import RegisterCommand


def registration_command(**overrides: str) -> dict[str, str]:
    command = {
        "email": "customer@example.com",
        "first_name": "Amina",
        "last_name": "Khan",
        "password": "SecureBank1!",
    }
    command.update(overrides)
    return command


def test_registration_accepts_and_normalizes_customer_details():
    command = RegisterCommand(
        **registration_command(
            email="  CUSTOMER@EXAMPLE.COM  ",
            first_name="  Amina ",
            last_name=" Khan  ",
        )
    )

    assert command.email == "customer@example.com"
    assert command.first_name == "Amina"
    assert command.last_name == "Khan"


@pytest.mark.parametrize(
    "password",
    [
        "Short1!",
        "lowercase123!",
        "UPPERCASE123!",
        "NoNumbersHere!",
        "NoSpecialChar1",
    ],
)
def test_registration_rejects_weak_passwords(password: str):
    with pytest.raises(ValidationError):
        RegisterCommand(**registration_command(password=password))


@pytest.mark.parametrize("field", ["first_name", "last_name"])
def test_registration_rejects_blank_names(field: str):
    with pytest.raises(ValidationError):
        RegisterCommand(**registration_command(**{field: "   "}))
