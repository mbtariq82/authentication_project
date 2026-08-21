from datetime import datetime

from domain.card import Card, AuthenticatedUserContext
from domain.account import Account
from domain.user import User


class TestCard:

    def test_creates_card_with_required_fields(self):
        expiry_date = datetime(2029, 12, 1)

        card = Card(
            account_id=1,
            card_number="1234567890123456",
            expiry_date=expiry_date,
            cvc="123",
            status="ACTIVE",
        )

        assert card.account_id == 1
        assert card.card_number == "1234567890123456"
        assert card.expiry_date == expiry_date
        assert card.cvc == "123"
        assert card.status == "ACTIVE"
        assert card.id is None
        assert card.created_at is None

    def test_creates_card_with_optional_fields(self):
        expiry_date = datetime(2029, 12, 1)
        created_at = datetime(2026, 8, 20, 10, 30)

        card = Card(
            account_id=1,
            card_number="1234567890123456",
            expiry_date=expiry_date,
            cvc="123",
            status="ACTIVE",
            id=10,
            created_at=created_at,
        )

        assert card.id == 10
        assert card.created_at == created_at

    def test_card_is_slotted(self):
        card = Card(
            account_id=1,
            card_number="1234567890123456",
            expiry_date=datetime(2029, 12, 1),
            cvc="123",
            status="ACTIVE",
        )

        assert not hasattr(card, "__dict__")


class TestAuthenticatedUserContext:

    def test_creates_context(self):
        user = User(
            id=1,
            email="john@example.com",
            first_name="John",
            last_name="Smith",
        )

        account = Account(
            user_id=1,
            balance=1000,
        )

        context = AuthenticatedUserContext(
            user=user,
            account=account,
        )

        assert context.user is user
        assert context.account is account

    def test_context_is_slotted(self):
        user = User(
            id=1,
            email="john@example.com",
            first_name="John",
            last_name="Smith",
        )

        account = Account(
            user_id=1,
            balance=1000,
        )

        context = AuthenticatedUserContext(
            user=user,
            account=account,
        )

        assert not hasattr(context, "__dict__")