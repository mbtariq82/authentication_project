from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from dependencies.loan import (
    get_loan_repository,
    get_loan_service,
    get_loan_uow
)
from repositories.abstract_loan_repository import AbstractLoanRepository
from repositories.sqlalchemy_loan_repository import SQLAlchemyLoanRepository
from services.loan_service import LoanService
from unit_of_work.abstract_loan_unit_of_work import AbstractLoanUnitOfWork
from unit_of_work.sqlalchemy_loan_unit_of_work import SqlAlchemyLoanUnitOfWork


class TestGetLoanRepository:

    def test_returns_sqlalchemy_loan_repository(self):
        session = MagicMock()

        repository = get_loan_repository(session)

        assert isinstance(repository, SQLAlchemyLoanRepository)
        assert isinstance(repository, AbstractLoanRepository)
        assert repository.session is session


class TestGetLoanService:

    def test_returns_loan_service(self):
        uow = MagicMock(spec=AbstractLoanUnitOfWork)

        service = get_loan_service(uow)

        assert isinstance(service, LoanService)
        assert service.uow is uow


class TestGetLoanUow:

    @pytest.mark.asyncio
    @patch("dependencies.loan.SqlAlchemyLoanUnitOfWork")
    async def test_creates_uow_with_session(
        self,
        mock_uow_class,
    ):
        session = MagicMock()

        mock_uow = MagicMock()
        mock_uow_class.return_value.__aenter__ = AsyncMock(
            return_value=mock_uow
        )
        mock_uow_class.return_value.__aexit__ = AsyncMock()

        generator = get_loan_uow(session)

        uow = await generator.__anext__()

        assert uow is mock_uow
        mock_uow_class.assert_called_once_with(session)

        await generator.aclose()