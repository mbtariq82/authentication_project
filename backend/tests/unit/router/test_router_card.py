from decimal import Decimal
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from domain.card import AuthenticatedUserContext
from router.card import (
    get_unmasked_card,
    get_user_card,
    create_card,
    freeze_card,
    block_card,
)
from schemas.card import (
    CardDetailsRequest,
    CardDetailsResponse,
    CardResponse,
    CardStatusResponse,
)


@pytest.fixture
def card_service():
    service = MagicMock()

    service.get_unmasked_card = AsyncMock()
    service.get_user_card = AsyncMock()
    service.create_card = AsyncMock()
    service.toggle_card_status = AsyncMock()
    service.block_card = AsyncMock()

    return service


@pytest.fixture
def user_context():
    context = MagicMock(spec=AuthenticatedUserContext)

    context.account.id = 100
    context.user.id = 50
    context.user.email = "john@example.com"

    return context


@pytest.fixture
def admin():
    return MagicMock()


class TestGetUnmaskedCard:

    @pytest.mark.asyncio
    async def test_get_unmasked_card(
        self,
        card_service,
        user_context,
    ):
        request = CardDetailsRequest(
            password="password123",
        )

        expected_response = CardDetailsResponse(
            card_number="1234567890123456",
            expiry_date=datetime(2029, 12, 1),
            cvc="123",
        )

        card_service.get_unmasked_card.return_value = expected_response

        result = await get_unmasked_card(
            request=request,
            context=user_context,
            service=card_service,
        )

        assert result == expected_response

        card_service.get_unmasked_card.assert_awaited_once_with(
            account_id=100,
            email="john@example.com",
            password="password123",
        )


class TestGetUserCard:

    @pytest.mark.asyncio
    async def test_get_user_card(
        self,
        card_service,
        user_context,
    ):
        expected_response = CardDetailsResponse(
            card_number="1234567890123456",
            expiry_date=datetime(2029, 12, 1),
            cvc="123",
        )

        card_service.get_user_card.return_value = expected_response

        result = await get_user_card(
            context=user_context,
            service=card_service,
        )

        assert result == expected_response

        card_service.get_user_card.assert_awaited_once_with(
            account_id=100,
            user_id=50,
        )


class TestCreateCard:

    @pytest.mark.asyncio
    async def test_create_card(
        self,
        card_service,
        user_context,
    ):
        expected_response = CardResponse(
            id=1,
            account_id=100,
            card_number="1234567890123456",
            cvc="123",
            expiry_date=datetime(2029, 12, 1),
            status="ACTIVE",
            created_at=datetime(2026, 8, 20, 12, 0),
        )

        card_service.create_card.return_value = expected_response

        result = await create_card(
            context=user_context,
            service=card_service,
        )

        assert result == expected_response

        card_service.create_card.assert_awaited_once_with(
            account_id=100,
            user_id=50,
        )


class TestFreezeCard:

    @pytest.mark.asyncio
    async def test_freeze_card(
        self,
        card_service,
        user_context,
    ):
        expected_response = CardStatusResponse(
            status="FROZEN",
        )

        card_service.toggle_card_status.return_value = expected_response

        result = await freeze_card(
            context=user_context,
            service=card_service,
        )

        assert result == expected_response

        card_service.toggle_card_status.assert_awaited_once_with(
            account_id=100,
            user_id=50,
        )


class TestBlockCard:

    @pytest.mark.asyncio
    async def test_block_card(
        self,
        card_service,
        admin,
    ):
        expected_response = CardStatusResponse(
            status="BLOCKED",
        )

        card_service.block_card.return_value = expected_response

        result = await block_card(
            card_id=25,
            current_user=admin,
            service=card_service,
        )

        assert result == expected_response

        card_service.block_card.assert_awaited_once_with(25)