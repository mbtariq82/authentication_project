from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from domain.card import AuthenticatedUserContext
from router.loan import (
    apply_for_loan,
    get_pending_loans,
    decide_loan,
    get_my_loans,
    repay_loan,
)
from schemas.loan import (
    LoanApplicationRequest,
    LoanApplicationResponse,
    LoanDecisionRequest,
    LoanListResponse,
    LoanRepaymentRequest,
    LoanRepaymentResponse,
)


@pytest.fixture
def loan_service():
    service = MagicMock()

    service.apply_for_loan = AsyncMock()
    service.get_pending_loans = AsyncMock()
    service.update_loan_status = AsyncMock()
    service.get_user_loans = AsyncMock()
    service.repay_loan = AsyncMock()

    return service


@pytest.fixture
def user_context():
    context = MagicMock(spec=AuthenticatedUserContext)
    context.account.id = 100

    return context


class TestApplyForLoan:

    @pytest.mark.asyncio
    async def test_apply_for_loan(
        self,
        loan_service,
        user_context,
    ):
        request = LoanApplicationRequest(
            loan_type="House",
            loan_amount=Decimal("100000"),
            monthly_income=Decimal("5000"),
            monthly_expenses=Decimal("2000"),
            duration=120,
        )

        expected_response = LoanApplicationResponse(
            eligible=True,
            status="PENDING",
            loan_id=1,
        )

        loan_service.apply_for_loan.return_value = expected_response

        result = await apply_for_loan(
            request=request,
            user_context=user_context,
            loan_service=loan_service,
        )

        assert result == expected_response

        loan_service.apply_for_loan.assert_awaited_once_with(
            request=request,
            user_context=user_context,
        )


class TestGetPendingLoans:

    @pytest.mark.asyncio
    async def test_get_pending_loans(self, loan_service):

        expected_response = LoanListResponse(loans=[])

        loan_service.get_pending_loans.return_value = expected_response

        admin = MagicMock()

        result = await get_pending_loans(
            admin=admin,
            loan_service=loan_service,
        )

        assert result == expected_response

        loan_service.get_pending_loans.assert_awaited_once_with()


class TestDecideLoan:

    @pytest.mark.asyncio
    async def test_decide_loan(
        self,
        loan_service,
    ):
        request = LoanDecisionRequest(
            status="ACCEPTED",
        )

        expected_response = LoanApplicationResponse(
            eligible=True,
            status="ACCEPTED",
            loan_id=10,
        )

        loan_service.update_loan_status.return_value = expected_response

        admin = MagicMock()

        result = await decide_loan(
            loan_id=10,
            request=request,
            admin=admin,
            loan_service=loan_service,
        )

        assert result == expected_response

        loan_service.update_loan_status.assert_awaited_once_with(
            loan_id=10,
            status="ACCEPTED",
        )

    @pytest.mark.asyncio
    async def test_decide_loan_rejected(
        self,
        loan_service,
    ):
        request = LoanDecisionRequest(
            status="REJECTED",
        )

        expected_response = LoanApplicationResponse(
            eligible=True,
            status="REJECTED",
            loan_id=10,
        )

        loan_service.update_loan_status.return_value = expected_response

        admin = MagicMock()

        result = await decide_loan(
            loan_id=10,
            request=request,
            admin=admin,
            loan_service=loan_service,
        )

        assert result == expected_response

        loan_service.update_loan_status.assert_awaited_once_with(
            loan_id=10,
            status="REJECTED",
        )


class TestGetMyLoans:

    @pytest.mark.asyncio
    async def test_get_my_loans(
        self,
        loan_service,
        user_context,
    ):
        expected_response = LoanListResponse(
            loans=[],
        )

        loan_service.get_user_loans.return_value = expected_response

        result = await get_my_loans(
            user_context=user_context,
            loan_service=loan_service,
        )

        assert result == expected_response

        loan_service.get_user_loans.assert_awaited_once_with(
            user_context=user_context,
        )


class TestRepayLoan:

    @pytest.mark.asyncio
    async def test_repay_loan(
        self,
        loan_service,
        user_context,
    ):
        request = LoanRepaymentRequest(
            loan_id=10,
            amount=Decimal("500"),
        )

        expected_response = LoanRepaymentResponse(
            loan_id=10,
            repayment_amount=Decimal("500"),
            remaining_amount=Decimal("9500"),
            status="ACCEPTED",
        )

        loan_service.repay_loan.return_value = expected_response

        result = await repay_loan(
            request=request,
            user_context=user_context,
            loan_service=loan_service,
        )

        assert result == expected_response

        loan_service.repay_loan.assert_awaited_once_with(
            request=request,
            user_context=user_context,
        )