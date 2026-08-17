import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from domain.account import Account
from domain.card import Card
from domain.user import User
from exceptions import AccountNotFoundError, CardNotFoundError, InvalidCardStatusError
from schemas.card import CardResponse, CardDetailsResponse, CardStatusResponse
from services.card_service import CardService

def test_generate_cvc():
    service = CardService(None)

    for _ in range(100):
        cvc = service._generate_cvc()

        assert len(cvc) == 3
        assert cvc.isdigit()

def test_generate_card_number():
    service = CardService(None)

    for _ in range(100):
        card_number = service._generate_card_number()

        assert len(card_number) == 16
        assert card_number.isdigit()

        total = 0

        for i, digit in enumerate(card_number):
            value = int(digit)

            if i % 2 == 0:
                value *= 2

                if value > 9:
                    value -= 9

            total += value

        assert total % 10 == 0

@pytest.mark.asyncio
async def test_generate_unique_card_number():
    uow = MagicMock()
    uow.card_repository.card_number_exists = AsyncMock(return_value=False)

    service = CardService(uow)

    service._generate_card_number = MagicMock(
        return_value="1234567890123456"
    )

    result = await service._generate_unique_card_number()

    assert result == "1234567890123456"

    uow.card_repository.card_number_exists.assert_awaited_once_with(
        "1234567890123456"
    )

@pytest.mark.asyncio
async def test_generate_unique_card_number_retries():
    uow = MagicMock()

    uow.card_repository.card_number_exists = AsyncMock(
        side_effect=[True, False]
    )

    service = CardService(uow)

    service._generate_card_number = MagicMock(
        side_effect=[
            "1111111111111111",
            "2222222222222222",
        ]
    )

    result = await service._generate_unique_card_number()

    assert result == "2222222222222222"

    assert service._generate_card_number.call_count == 2

    assert uow.card_repository.card_number_exists.await_count == 2

@pytest.mark.asyncio
async def test_create_card():
    uow = MagicMock()

    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock()
    uow.commit = AsyncMock()

    uow.card_repository.get_account_by_user = AsyncMock()
    uow.card_repository.get_active_or_frozen_card = AsyncMock()
    uow.card_repository.create_card = AsyncMock()

    account = Account(
        id=1,
        user_id=10,
        balance=0,
    )

    uow.card_repository.get_account_by_user.return_value = account
    uow.card_repository.get_active_or_frozen_card.return_value = None

    created_card = Card(
        id=5,
        account_id=1,
        card_number="1234567890123456",
        expiry_date=datetime.now(timezone.utc),
        cvc="123",
        status="ACTIVE",
        created_at=datetime.now(timezone.utc),
    )

    uow.card_repository.create_card.return_value = created_card

    service = CardService(uow)

    service._generate_unique_card_number = AsyncMock(
        return_value="1234567890123456"
    )

    service._generate_cvc = MagicMock(
        return_value="123"
    )

    result = await service.create_card(
        account_id=1,
        user_id=10,
    )

    assert isinstance(result, CardResponse)
    assert result.id == 5
    assert result.status == "ACTIVE"
    assert result.account_id == 1
    assert result.card_number == "1234567890123456"
    assert result.cvc == "123"

    uow.card_repository.get_account_by_user.assert_awaited_once_with(1, 10)

    uow.card_repository.get_active_or_frozen_card.assert_awaited_once_with(1, 10)

    service._generate_unique_card_number.assert_awaited_once()
    service._generate_cvc.assert_called_once()

    uow.card_repository.create_card.assert_awaited_once()

    uow.commit.assert_awaited()

@pytest.mark.asyncio
async def test_create_card_account_not_found():
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)

    card_repository = MagicMock()
    card_repository.get_account_by_user = AsyncMock(return_value=None)

    uow.card_repository = card_repository

    service = CardService(uow)

    with pytest.raises(AccountNotFoundError):
        await service.create_card(
            account_id=1,
            user_id=10,
        )

    card_repository.get_account_by_user.assert_awaited_once_with(1, 10)
    card_repository.create_card.assert_not_called()

def test_mask_card_number():
    uow = MagicMock()
    service = CardService(uow)

    result = service._mask_card_number("1234567890123456")

    assert result == "************3456"

def test_mask_cvc():
    uow = MagicMock()
    service = CardService(uow)

    result = service._mask_cvc("123")

    assert result == "***"

@pytest.mark.asyncio
async def test_get_user_card():
    card_repository = MagicMock()

    
    card = Card(
        id=1,
        account_id=10,
        card_number="1234567890123456",
        cvc="123",
        status="ACTIVE",
        expiry_date=datetime(2028, 8, 31, tzinfo=timezone.utc),
    )

    card_repository.get_active_or_frozen_card = AsyncMock(
        return_value=card
    )

    uow = MagicMock()
    uow.card_repository = card_repository
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)

    service = CardService(uow)

    result = await service._get_user_card(
        account_id=10,
        user_id=5,
    )

    assert result is card

    card_repository.get_active_or_frozen_card.assert_awaited_once_with(
        10,
        5,
    )

@pytest.mark.asyncio
async def test_get_user_card_not_found():
    card_repository = MagicMock()

    card_repository.get_active_or_frozen_card = AsyncMock(
        return_value=None
    )

    uow = MagicMock()
    uow.card_repository = card_repository
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)

    service = CardService(uow)

    with pytest.raises(CardNotFoundError):
        await service._get_user_card(
            account_id=10,
            user_id=5,
        )

    card_repository.get_active_or_frozen_card.assert_awaited_once_with(
        10,
        5,
    )

@pytest.mark.asyncio
async def test_get_user_card():
    uow = MagicMock()
    service = CardService(uow)

    card = Card(
        id=1,
        account_id=10,
        card_number="1234567890123456",
        expiry_date=datetime(2028, 8, 31, tzinfo=timezone.utc),
        cvc="123",
        status="ACTIVE",
    )

    service._get_user_card = AsyncMock(return_value=card)

    result = await service.get_user_card(
        account_id=10,
        user_id=5,
    )

    assert isinstance(result, CardDetailsResponse)
    assert result.card_number == "************3456"
    assert result.expiry_date == card.expiry_date
    assert result.cvc == "***"

    service._get_user_card.assert_awaited_once_with(
        10,
        5,
    )

@pytest.mark.asyncio
async def test_get_unmasked_card():
    uow = MagicMock()

    user = User(
        id=10,
        first_name="John",
        last_name="Doe",
        email="test@informationtechconsultants.co.uk",
        hashed_password="hashed_password",
    )

    card = Card(
        id=1,
        account_id=10,
        card_number="1234567890123456",
        expiry_date=datetime(2028, 8, 31, tzinfo=timezone.utc),
        cvc="123",
        status="ACTIVE",
    )

    uow.user_repository.get_by_email = AsyncMock(
        return_value=user
    )

    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)

    service = CardService(uow)

    service._get_user_card = AsyncMock(
        return_value=card
    )

    with patch(
        "services.card_service.pwd_context.verify",
        return_value=True,
    ):
        result = await service.get_unmasked_card(
            account_id=10,
            email="test@example.com",
            password="password123",
        )

    assert isinstance(result, CardDetailsResponse)
    assert result.card_number == "1234567890123456"
    assert result.expiry_date == card.expiry_date
    assert result.cvc == "123"

    uow.user_repository.get_by_email.assert_awaited_once_with(
        "test@example.com"
    )

    service._get_user_card.assert_awaited_once_with(
        10,
        10,
    )

@pytest.mark.asyncio
async def test_toggle_card_status_frozen_to_active():
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)
    uow.commit = AsyncMock()

    card = Card(
        id=1,
        account_id=10,
        card_number="1234567890123456",
        expiry_date=datetime(2028, 8, 31, tzinfo=timezone.utc),
        cvc="123",
        status="FROZEN",
    )

    service = CardService(uow)

    service._get_user_card = AsyncMock(return_value=card)
    uow.card_repository.update_card = AsyncMock(return_value=card)

    result = await service.toggle_card_status(10, 5)

    assert isinstance(result, CardStatusResponse)
    assert result.status == "Activated."
    assert card.status == "ACTIVE"

    service._get_user_card.assert_awaited_once_with(10, 5)
    uow.card_repository.update_card.assert_awaited_once_with(card)
    uow.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_toggle_card_status_active_to_frozen():
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)
    uow.commit = AsyncMock()

    card = Card(
        id=1,
        account_id=10,
        card_number="1234567890123456",
        expiry_date=datetime(2028, 8, 31, tzinfo=timezone.utc),
        cvc="123",
        status="ACTIVE",
    )

    service = CardService(uow)

    service._get_user_card = AsyncMock(return_value=card)
    uow.card_repository.update_card = AsyncMock(return_value=card)

    result = await service.toggle_card_status(10, 5)

    assert isinstance(result, CardStatusResponse)
    assert result.status == "Frozen."
    assert card.status == "FROZEN"

    service._get_user_card.assert_awaited_once_with(10, 5)
    uow.card_repository.update_card.assert_awaited_once_with(card)
    uow.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_toggle_card_status_invalid_status():
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)

    card = Card(
        id=1,
        account_id=10,
        card_number="1234567890123456",
        expiry_date=datetime(2028, 8, 31, tzinfo=timezone.utc),
        cvc="123",
        status="CANCELLED",
    )

    service = CardService(uow)

    service._get_user_card = AsyncMock(return_value=card)

    with pytest.raises(InvalidCardStatusError):
        await service.toggle_card_status(10, 5)

    uow.card_repository.update_card.assert_not_called()

@pytest.mark.asyncio
async def test_block_card():
    card_repository = MagicMock()
    card_repository.get_card_by_id = AsyncMock()
    card_repository.update_card = AsyncMock()

    uow = MagicMock()
    uow.card_repository = card_repository
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)
    uow.commit = AsyncMock()

    card = Card(
        id=4,
        account_id=1,
        card_number="1234567890123456",
        expiry_date=datetime(2028, 8, 31, tzinfo=timezone.utc),
        cvc="123",
        status="ACTIVE",
    )

    card_repository.get_card_by_id.return_value = card
    card_repository.update_card.return_value = card

    service = CardService(uow)

    result = await service.block_card(card_id=4)

    assert isinstance(result, CardStatusResponse)
    assert result.status == "CANCELLED"

    assert card.status == "CANCELLED"

    card_repository.get_card_by_id.assert_awaited_once_with(4)
    card_repository.update_card.assert_awaited_once_with(card)
    uow.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_block_card_not_found():
    card_repository = MagicMock()
    card_repository.get_card_by_id = AsyncMock(return_value=None)
    card_repository.update_card = AsyncMock()

    uow = MagicMock()
    uow.card_repository = card_repository
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=False)
    uow.commit = AsyncMock()

    service = CardService(uow)

    with pytest.raises(CardNotFoundError):
        await service.block_card(card_id=4)

    card_repository.get_card_by_id.assert_awaited_once_with(4)
    card_repository.update_card.assert_not_called()
    uow.commit.assert_not_awaited()

