from dataclasses import dataclass

from enums import Role


@dataclass(slots=True)
class User:
    email: str
    id: int | None = None
    role: Role = Role.USER
    hashed_password: str | None = None
    google_subject: str | None = None

    @classmethod
    def register_with_password(
        cls,
        email: str,
        hashed_password: str,
    ) -> "User":
        return cls(
            id=None,
            email=email,
            hashed_password=hashed_password,
        )

    def link_google_identity(self, google_subject: str) -> None:
        if (
            self.google_subject is not None
            and self.google_subject != google_subject
        ):
            raise ValueError("User is already linked to another Google identity")

        self.google_subject = google_subject