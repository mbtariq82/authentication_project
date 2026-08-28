from unittest.mock import AsyncMock, MagicMock

import pytest

from repositories.sqlalchemy_loan_repository import SQLAlchemyLoanRepository
from models.loan import LoanRow


@pytest.fixture
def session():
    return AsyncMock()


@pytest.fixture
def repository(session):
    return SQLAlchemyLoanRepository(session)


class TestSQLAlchemyLoanRepository:

    @pytest.mark.asyncio
    async def test_create(self, repository, session):
        loan = MagicMock(spec=LoanRow)

        result = await repository.create(loan)

        session.add.assert_called_once_with(loan)
        session.flush.assert_awaited_once()
        assert result is loan

    @pytest.mark.asyncio
    async def test_get_loan_by_id(self, repository, session):
        loan = MagicMock(spec=LoanRow)

        execute_result = MagicMock()
        execute_result.scalar_one_or_none.return_value = loan

        session.execute = AsyncMock(return_value=execute_result)

        result = await repository.get_loan_by_id(1)

        assert result is loan
        session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_loan_by_id_returns_none_when_not_found(
        self,
        repository,
        session,
    ):
        execute_result = MagicMock()
        execute_result.scalar_one_or_none.return_value = None

        session.execute = AsyncMock(return_value=execute_result)

        result = await repository.get_loan_by_id(999)

        assert result is None
        session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_loans_by_account_id(self, repository, session):
        loans = [
            MagicMock(spec=LoanRow),
            MagicMock(spec=LoanRow),
        ]

        execute_result = MagicMock()
        execute_result.scalars.return_value.all.return_value = loans

        session.execute = AsyncMock(return_value=execute_result)

        result = await repository.get_loans_by_account_id(10)

        assert result == loans
        assert len(result) == 2
        session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_loans_by_account_id_returns_empty_list(
        self,
        repository,
        session,
    ):
        execute_result = MagicMock()
        execute_result.scalars.return_value.all.return_value = []

        session.execute = AsyncMock(return_value=execute_result)

        result = await repository.get_loans_by_account_id(999)

        assert result == []
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_pending_loans(self, repository, session):
        loans = [
            MagicMock(spec=LoanRow),
            MagicMock(spec=LoanRow),
        ]

        execute_result = MagicMock()
        execute_result.scalars.return_value.all.return_value = loans

        session.execute = AsyncMock(return_value=execute_result)

        result = await repository.get_pending_loans()

        assert result == loans
        assert len(result) == 2
        session.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_pending_loans_returns_empty_list(
        self,
        repository,
        session,
    ):
        execute_result = MagicMock()
        execute_result.scalars.return_value.all.return_value = []

        session.execute = AsyncMock(return_value=execute_result)

        result = await repository.get_pending_loans()

        assert result == []
        assert isinstance(result, list)