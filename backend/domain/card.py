from dataclasses import dataclass
from datetime import datetime

from domain.account import Account
from domain.user import User

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
    user: User
    account: Account