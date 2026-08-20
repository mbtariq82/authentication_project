from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from enums import AccountStatus
from models.account import AccountRow
from repositories.sqlalchemy_account_repository import SqlAlchemyAccountRepository


@pytest.mark.asyncio
async def test_get_by_account_number_and_sort_code_returns_active_account():
    session = MagicMock()
    row = AccountRow(
        id=2,
        user_id=4,
        account_number="12345678",
        sort_code="20-10-30",
        balance=Decimal("25.00"),
        account_status=AccountStatus.APPROVED.value,
        is_deleted=False,
    )
    query_result = MagicMock()
    query_result.scalar_one_or_none.return_value = row
    session.execute = AsyncMock(return_value=query_result)

    repository = SqlAlchemyAccountRepository(session)

    account = await repository.get_by_account_number_and_sort_code(
        "12345678",
        "20-10-30",
    )

    assert account is not None
    assert account.id == 2
    assert account.account_number == "12345678"
    assert account.sort_code == "20-10-30"
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_account_number_and_sort_code_returns_none_when_not_active():
    session = MagicMock()
    query_result = MagicMock()
    query_result.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=query_result)

    repository = SqlAlchemyAccountRepository(session)

    account = await repository.get_by_account_number_and_sort_code(
        "12345678",
        "20-10-30",
    )

    assert account is None
    session.execute.assert_awaited_once()