import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from domain.card import Card
from models.card import CardRow
from models.account import AccountRow
from repositories.sqlalchemy_card_repository import SqlAlchemyCardRepository

def test_to_domain():
    created_at = datetime.now(timezone.utc)
    expiry_date = datetime(2028, 8, 31, tzinfo=timezone.utc)

    row = CardRow(
        id=4,
        account_id=1,
        card_number="1234567890123456",
        expiry_date=expiry_date,
        cvc="123",
        status="ACTIVE",
        created_at=created_at,
    )

    expected = Card(
        id=4,
        account_id=1,
        card_number="1234567890123456",
        expiry_date=expiry_date,
        cvc="123",
        status="ACTIVE",
        created_at=created_at,
    )

    result = SqlAlchemyCardRepository._to_domain(row)

    assert result == expected

@pytest.mark.asyncio
async def test_card_number_exists_returns_true():
    session = MagicMock()

    result = MagicMock()
    result.scalar_one_or_none.return_value = 1

    session.execute = AsyncMock(return_value=result)

    repository = SqlAlchemyCardRepository(session)

    exists = await repository.card_number_exists(
        "1234567890123456"
    )

    assert exists is True

@pytest.mark.asyncio
async def test_card_number_exists_returns_false():
    session = MagicMock()

    result = MagicMock()
    result.scalar_one_or_none.return_value = None

    session.execute = AsyncMock(return_value=result)

    repository = SqlAlchemyCardRepository(session)

    exists = await repository.card_number_exists(
        "1234567890123456"
    )

    assert exists is False


@pytest.mark.asyncio
async def test_get_account_by_user_returns_account():
    session = MagicMock()

    account = AccountRow(
        id=1,
        user_id=10,
        balance=100.00,
    )

    result = MagicMock()
    result.scalar_one_or_none.return_value = account

    session.execute = AsyncMock(return_value=result)

    repository = SqlAlchemyCardRepository(session)

    result = await repository.get_account_by_user(
        account_id=1,
        user_id=10,
    )

    assert result == account
    session.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_account_by_user_returns_none():
    session = MagicMock()

    result = MagicMock()
    result.scalar_one_or_none.return_value = None

    session.execute = AsyncMock(return_value=result)

    repository = SqlAlchemyCardRepository(session)

    result = await repository.get_account_by_user(
        account_id=999,
        user_id=10,
    )

    assert result is None
    session.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_active_or_frozen_card_returns_card():
    session = MagicMock()

    card_row = CardRow(
        id=1,
        account_id=10,
        card_number="1234567890123456",
        expiry_date=datetime(2028, 8, 31, tzinfo=timezone.utc),
        cvc="123",
        status="ACTIVE",
        created_at=datetime.now(timezone.utc),
    )

    result = MagicMock()
    result.scalar_one_or_none.return_value = card_row

    session.execute = AsyncMock(return_value=result)

    repository = SqlAlchemyCardRepository(session)

    card = await repository.get_active_or_frozen_card(
        account_id=10,
        user_id=1,
    )

    assert isinstance(card, Card)
    assert card.id == 1
    assert card.account_id == 10
    assert card.card_number == "1234567890123456"
    assert card.cvc == "123"
    assert card.status == "ACTIVE"

    session.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_active_or_frozen_card_returns_none():
    session = MagicMock()

    result = MagicMock()
    result.scalar_one_or_none.return_value = None

    session.execute = AsyncMock(return_value=result)

    repository = SqlAlchemyCardRepository(session)

    card = await repository.get_active_or_frozen_card(
        account_id=10,
        user_id=1,
    )

    assert card is None
    session.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_create_card():
    session = MagicMock()

    session.add = MagicMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()

    repository = SqlAlchemyCardRepository(session)

    expiry_date = datetime(2028, 8, 31, tzinfo=timezone.utc)
    created_at = datetime.now(timezone.utc)

    card = Card(
        account_id=1,
        card_number="1234567890123456",
        expiry_date=expiry_date,
        cvc="123",
        status="ACTIVE",
        created_at=created_at,
    )

    result = await repository.create_card(card)

    session.add.assert_called_once()

    created_row = session.add.call_args[0][0]

    assert isinstance(created_row, CardRow)
    assert created_row.account_id == 1
    assert created_row.card_number == "1234567890123456"
    assert created_row.expiry_date == expiry_date
    assert created_row.cvc == "123"
    assert created_row.status == "ACTIVE"

    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(created_row)

    assert isinstance(result, Card)
    assert result.account_id == 1
    assert result.card_number == "1234567890123456"
    assert result.cvc == "123"
    assert result.status == "ACTIVE"


@pytest.mark.asyncio
async def test_get_user_cards_returns_active_card():
    session = MagicMock()

    expiry_date = datetime(2028, 8, 31, tzinfo=timezone.utc)
    created_at = datetime.now(timezone.utc)
    card_row = CardRow(
        id=4,
        account_id=1,
        card_number="1234567890123456",
        expiry_date=expiry_date,
        cvc="123",
        status="ACTIVE",
        created_at=created_at,
    )

    result = MagicMock()
    result.scalar_one_or_none.return_value = card_row

    session.execute = AsyncMock(return_value=result)

    repository = SqlAlchemyCardRepository(session)

    card = await repository.get_user_cards(
        account_id=1,
        user_id=10,
    )

    assert isinstance(card, Card)
    assert card.id == 4
    assert card.account_id == 1
    assert card.card_number == "1234567890123456"
    assert card.cvc == "123"
    assert card.status == "ACTIVE"

    session.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_user_cards_returns_none_when_no_active_card():
    session = MagicMock()

    result = MagicMock()
    result.scalar_one_or_none.return_value = None

    session.execute = AsyncMock(return_value=result)

    repository = SqlAlchemyCardRepository(session)

    card = await repository.get_user_cards(
        account_id=1,
        user_id=10,
    )

    assert card is None

    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_card_by_id_returns_card():
    session = MagicMock()

    card_row = CardRow(
        id=4,
        account_id=1,
        card_number="1234567890123456",
        expiry_date=datetime(2028, 8, 31, tzinfo=timezone.utc),
        cvc="123",
        status="ACTIVE",
        created_at=datetime.now(timezone.utc),
    )

    result = MagicMock()
    result.scalar_one_or_none.return_value = card_row

    session.execute = AsyncMock(return_value=result)

    repository = SqlAlchemyCardRepository(session)

    card = await repository.get_card_by_id(4)

    assert isinstance(card, Card)
    assert card.id == 4
    assert card.account_id == 1
    assert card.card_number == "1234567890123456"
    assert card.cvc == "123"
    assert card.status == "ACTIVE"

    session.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_card_by_id_returns_none():
    session = MagicMock()

    result = MagicMock()
    result.scalar_one_or_none.return_value = None

    session.execute = AsyncMock(return_value=result)

    repository = SqlAlchemyCardRepository(session)

    card = await repository.get_card_by_id(999)

    assert card is None

    session.execute.assert_awaited_once()

@pytest.mark.asyncio
async def test_update_card():
    session = MagicMock()

    card_row = CardRow(
        id=4,
        account_id=1,
        card_number="1234567890123456",
        expiry_date=datetime(2028, 8, 31, tzinfo=timezone.utc),
        cvc="123",
        status="ACTIVE",
        created_at=datetime.now(timezone.utc),
    )

    result = MagicMock()
    result.scalar_one.return_value = card_row

    session.execute = AsyncMock(return_value=result)
    session.flush = AsyncMock()
    session.refresh = AsyncMock()

    repository = SqlAlchemyCardRepository(session)

    card = Card(
        id=4,
        account_id=1,
        card_number="1234567890123456",
        expiry_date=card_row.expiry_date,
        cvc="123",
        status="CANCELLED",
        created_at=card_row.created_at,
    )

    updated_card = await repository.update_card(card)

    assert card_row.status == "CANCELLED"

    session.execute.assert_awaited_once()
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(card_row)

    assert isinstance(updated_card, Card)
    assert updated_card.id == 4
    assert updated_card.account_id == 1
    assert updated_card.card_number == "1234567890123456"
    assert updated_card.cvc == "123"
    assert updated_card.status == "CANCELLED"