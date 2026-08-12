from dataclasses import dataclass

from enums import Role


@dataclass(slots=True)
class User:
    email: str
    first_name: str
    last_name: str
    id: int | None = None
    role: Role = Role.USER
    hashed_password: str | None = None

    @classmethod
    def register_with_password(
        cls,
        email: str,
        hashed_password: str,
        first_name: str,
        last_name: str,
    ) -> "User":
        return cls(
            id=None,
            email=email,
            first_name=first_name,
            last_name=last_name,
            hashed_password=hashed_password,
        )
