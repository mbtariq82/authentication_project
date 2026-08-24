from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

class AuthenticatedUser(Protocol):
    id: int
    email: str


class AuthenticatedAccount(Protocol):
    id: int


@dataclass(slots=True)
class Card:
    account_id: int
    card_number: str
    expiry_date: datetime
    cvc: str
    status: str
    id: int | None = None
    created_at: datetime | None = None

@dataclass(slots=True)
class AuthenticatedUserContext:
    user: AuthenticatedUser
    account: AuthenticatedAccount