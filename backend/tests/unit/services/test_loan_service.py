from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from domain.card import AuthenticatedUserContext
from exceptions import (
    InsufficientFundsError,
    InvalidLoanStatusError,
    InvalidRepaymentAmountError,
    LoanNotFoundError,
    PermissionDeniedError,
)
from schemas.loan import (
    LoanApplicationRequest,
    LoanRepaymentRequest,
)
from services.loan_service import LoanService


@pytest.fixture
def uow():
    uow = MagicMock()

    uow.loans = MagicMock()
    uow.account = MagicMock()
    uow.transaction = MagicMock()

    uow.loans.create = AsyncMock()
    uow.loans.get_loan_by_id = AsyncMock()
    uow.loans.get_loans_by_account_id = AsyncMock()
    uow.loans.get_pending_loans = AsyncMock()

    uow.account.debit = AsyncMock()
    uow.transaction.add = AsyncMock()

    return uow


@pytest.fixture
def service(uow):
    return LoanService(uow)


@pytest.fixture
def user_context():
    context = MagicMock(spec=AuthenticatedUserContext)
    context.account.id = 100

    return context


def make_loan(
    loan_id=1,
    account_id=100,
    loan_amount=Decimal("10000"),
    duration=12,
    loan_type="House",
    interest=5,
    emi=Decimal("856.07"),
    status="ACCEPTED",
):
    loan = MagicMock()

    loan.id = loan_id
    loan.account_id = account_id
    loan.loan_amount = loan_amount
    loan.duration = duration
    loan.loan_type = loan_type
    loan.interest = interest
    loan.emi = emi
    loan.current_loan_status = status

    return loan


class TestApplyForLoan:

    @pytest.mark.asyncio
    @patch("services.loan_service.get_interest_rate")
    @patch("services.loan_service.assess_loan")
    @patch("services.loan_service.calculate_emi")
    async def test_apply_for_loan_when_eligible(
        self,
        mock_calculate_emi,
        mock_assess_loan,
        mock_get_interest_rate,
        service,
        uow,
        user_context,
    ):
        request = LoanApplicationRequest(
            loan_type="House",
            loan_amount=Decimal("10000"),
            monthly_income=Decimal("5000"),
            monthly_expenses=Decimal("2000"),
            duration=12,
        )

        mock_get_interest_rate.return_value = 5
        mock_assess_loan.return_value = True
        mock_calculate_emi.return_value = Decimal("856.07")

        created_loan = make_loan(
            loan_id=123,
            account_id=100,
            loan_amount=Decimal("10000"),
            status="PENDING",
        )

        uow.loans.create.return_value = created_loan

        response = await service.apply_for_loan(
            request,
            user_context,
        )

        assert response.eligible is True
        assert response.status == "PENDING"
        assert response.loan_id == 123

        mock_get_interest_rate.assert_called_once_with("House")
        mock_assess_loan.assert_called_once()
        mock_calculate_emi.assert_called_once_with(
            loan_amount=Decimal("10000"),
            interest=5,
            duration=12,
        )

        uow.loans.create.assert_awaited_once()

        created_loan_argument = uow.loans.create.call_args.args[0]

        assert created_loan_argument.account_id == 100
        assert created_loan_argument.loan_amount == Decimal("10000")
        assert created_loan_argument.duration == 12
        assert created_loan_argument.current_loan_status == "PENDING"
        assert created_loan_argument.loan_type == "House"
        assert created_loan_argument.interest == 5
        assert created_loan_argument.emi == Decimal("856.07")

    @pytest.mark.asyncio
    @patch("services.loan_service.get_interest_rate")
    @patch("services.loan_service.assess_loan")
    async def test_apply_for_loan_when_not_eligible(
        self,
        mock_assess_loan,
        mock_get_interest_rate,
        service,
        uow,
        user_context,
    ):
        request = LoanApplicationRequest(
            loan_type="House",
            loan_amount=Decimal("100000"),
            monthly_income=Decimal("2000"),
            monthly_expenses=Decimal("1900"),
            duration=12,
        )

        mock_get_interest_rate.return_value = 5
        mock_assess_loan.return_value = False

        response = await service.apply_for_loan(
            request,
            user_context,
        )

        assert response.eligible is False
        assert response.status == "REJECTED"
        assert response.loan_id is None

        uow.loans.create.assert_not_awaited()

    @pytest.mark.asyncio
    @patch("services.loan_service.get_interest_rate")
    @patch("services.loan_service.assess_loan")
    async def test_apply_for_loan_does_not_create_loan_when_rejected(
        self,
        mock_assess_loan,
        mock_get_interest_rate,
        service,
        uow,
        user_context,
    ):
        request = LoanApplicationRequest(
            loan_type="Automobile",
            loan_amount=Decimal("50000"),
            monthly_income=Decimal("3000"),
            monthly_expenses=Decimal("2800"),
            duration=24,
        )

        mock_get_interest_rate.return_value = 6
        mock_assess_loan.return_value = False

        await service.apply_for_loan(
            request,
            user_context,
        )

        mock_get_interest_rate.assert_called_once_with("Automobile")
        mock_assess_loan.assert_called_once()
        uow.loans.create.assert_not_awaited()


class TestUpdateLoanStatus:

    @pytest.mark.asyncio
    async def test_update_loan_status(self, service, uow):
        loan = make_loan(
            loan_id=123,
            status="PENDING",
        )

        uow.loans.get_loan_by_id.return_value = loan

        response = await service.update_loan_status(
            loan_id=123,
            status="ACCEPTED",
        )

        assert loan.current_loan_status == "ACCEPTED"

        assert response.eligible is True
        assert response.status == "ACCEPTED"
        assert response.loan_id == 123

        uow.loans.get_loan_by_id.assert_awaited_once_with(123)

    @pytest.mark.asyncio
    async def test_update_loan_status_raises_when_loan_not_found(
        self,
        service,
        uow,
    ):
        uow.loans.get_loan_by_id.return_value = None

        with pytest.raises(LoanNotFoundError):
            await service.update_loan_status(
                loan_id=999,
                status="ACCEPTED",
            )

    @pytest.mark.asyncio
    async def test_update_loan_status_raises_when_loan_is_not_pending(
        self,
        service,
        uow,
    ):
        loan = make_loan(status="ACCEPTED")

        uow.loans.get_loan_by_id.return_value = loan

        with pytest.raises(InvalidLoanStatusError):
            await service.update_loan_status(
                loan_id=1,
                status="REJECTED",
            )

        assert loan.current_loan_status == "ACCEPTED"


class TestGetUserLoans:

    @pytest.mark.asyncio
    async def test_get_user_loans(
        self,
        service,
        uow,
        user_context,
    ):
        loans = [
            make_loan(
                loan_id=1,
                loan_amount=Decimal("10000"),
                loan_type="House",
                duration=12,
                interest=5,
                emi=Decimal("856.07"),
                status="ACCEPTED",
            ),
            make_loan(
                loan_id=2,
                loan_amount=Decimal("5000"),
                loan_type="Education",
                duration=24,
                interest=4,
                emi=Decimal("217.12"),
                status="PENDING",
            ),
        ]

        uow.loans.get_loans_by_account_id.return_value = loans

        response = await service.get_user_loans(user_context)

        uow.loans.get_loans_by_account_id.assert_awaited_once_with(
            account_id=100
        )

        assert len(response.loans) == 2

        assert response.loans[0].id == 1
        assert response.loans[0].loan_type == "House"
        assert response.loans[0].loan_amount == Decimal("10000")
        assert response.loans[0].duration == 12
        assert response.loans[0].interest == 5
        assert response.loans[0].emi == Decimal("856.07")
        assert response.loans[0].current_loan_status == "ACCEPTED"

        assert response.loans[1].id == 2
        assert response.loans[1].loan_type == "Education"

    @pytest.mark.asyncio
    async def test_get_user_loans_returns_empty_list(
        self,
        service,
        uow,
        user_context,
    ):
        uow.loans.get_loans_by_account_id.return_value = []

        response = await service.get_user_loans(user_context)

        assert response.loans == []


class TestGetPendingLoans:

    @pytest.mark.asyncio
    async def test_get_pending_loans(
        self,
        service,
        uow,
    ):
        loans = [
            make_loan(
                loan_id=1,
                status="PENDING",
            ),
            make_loan(
                loan_id=2,
                status="PENDING",
            ),
        ]

        uow.loans.get_pending_loans.return_value = loans

        response = await service.get_pending_loans()

        uow.loans.get_pending_loans.assert_awaited_once()

        assert len(response.loans) == 2
        assert response.loans[0].id == 1
        assert response.loans[0].current_loan_status == "PENDING"
        assert response.loans[1].id == 2

    @pytest.mark.asyncio
    async def test_get_pending_loans_returns_empty_list(
        self,
        service,
        uow,
    ):
        uow.loans.get_pending_loans.return_value = []

        response = await service.get_pending_loans()

        assert response.loans == []


class TestRepayLoan:

    @pytest.mark.asyncio
    async def test_repay_loan_partially(
        self,
        service,
        uow,
        user_context,
    ):
        loan = make_loan(
            loan_id=10,
            account_id=100,
            loan_amount=Decimal("10000"),
            status="ACCEPTED",
        )

        uow.loans.get_loan_by_id.return_value = loan

        request = LoanRepaymentRequest(
            loan_id=10,
            amount=Decimal("2500"),
        )

        response = await service.repay_loan(
            request,
            user_context,
        )

        assert loan.loan_amount == Decimal("7500")
        assert loan.current_loan_status == "ACCEPTED"

        assert response.loan_id == 10
        assert response.repayment_amount == Decimal("2500")
        assert response.remaining_amount == Decimal("7500")
        assert response.status == "ACCEPTED"

        uow.account.debit.assert_awaited_once_with(
            account_id=100,
            amount=Decimal("2500"),
        )

        uow.transaction.add.assert_awaited_once()

        transaction = uow.transaction.add.call_args.args[0]

        assert transaction.account_id == 100
        assert transaction.amount == Decimal("2500")
        assert transaction.reference == "LOAN-10"

    @pytest.mark.asyncio
    async def test_repay_loan_fully(
        self,
        service,
        uow,
        user_context,
    ):
        loan = make_loan(
            loan_id=10,
            account_id=100,
            loan_amount=Decimal("5000"),
            status="ACCEPTED",
        )

        uow.loans.get_loan_by_id.return_value = loan

        request = LoanRepaymentRequest(
            loan_id=10,
            amount=Decimal("5000"),
        )

        response = await service.repay_loan(
            request,
            user_context,
        )

        assert loan.loan_amount == Decimal("0")
        assert loan.current_loan_status == "PAID"

        assert response.loan_id == 10
        assert response.repayment_amount == Decimal("5000")
        assert response.remaining_amount == Decimal("0")
        assert response.status == "PAID"

    @pytest.mark.asyncio
    async def test_repay_loan_raises_when_loan_not_found(
        self,
        service,
        uow,
        user_context,
    ):
        uow.loans.get_loan_by_id.return_value = None

        request = LoanRepaymentRequest(
            loan_id=999,
            amount=Decimal("100"),
        )

        with pytest.raises(LoanNotFoundError):
            await service.repay_loan(
                request,
                user_context,
            )

        uow.account.debit.assert_not_awaited()
        uow.transaction.add.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_repay_loan_raises_when_user_does_not_own_loan(
        self,
        service,
        uow,
        user_context,
    ):
        loan = make_loan(
            loan_id=10,
            account_id=999,
            status="ACCEPTED",
        )

        uow.loans.get_loan_by_id.return_value = loan

        request = LoanRepaymentRequest(
            loan_id=10,
            amount=Decimal("100"),
        )

        with pytest.raises(PermissionDeniedError):
            await service.repay_loan(
                request,
                user_context,
            )

        uow.account.debit.assert_not_awaited()
        uow.transaction.add.assert_not_awaited()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "status",
        ["PENDING", "REJECTED", "PAID"],
    )
    async def test_repay_loan_raises_when_loan_not_accepted(
        self,
        status,
        service,
        uow,
        user_context,
    ):
        loan = make_loan(
            loan_id=10,
            account_id=100,
            status=status,
        )

        uow.loans.get_loan_by_id.return_value = loan

        request = LoanRepaymentRequest(
            loan_id=10,
            amount=Decimal("100"),
        )

        with pytest.raises(InvalidLoanStatusError):
            await service.repay_loan(
                request,
                user_context,
            )

        uow.account.debit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_repay_loan_raises_when_amount_exceeds_remaining_loan(
        self,
        service,
        uow,
        user_context,
    ):
        loan = make_loan(
            loan_id=10,
            account_id=100,
            loan_amount=Decimal("1000"),
            status="ACCEPTED",
        )

        uow.loans.get_loan_by_id.return_value = loan

        request = LoanRepaymentRequest(
            loan_id=10,
            amount=Decimal("1001"),
        )

        with pytest.raises(InvalidRepaymentAmountError):
            await service.repay_loan(
                request,
                user_context,
            )

        uow.account.debit.assert_not_awaited()
        uow.transaction.add.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_repay_loan_converts_insufficient_funds_to_invalid_amount(
        self,
        service,
        uow,
        user_context,
    ):
        loan = make_loan(
            loan_id=10,
            account_id=100,
            loan_amount=Decimal("1000"),
            status="ACCEPTED",
        )

        uow.loans.get_loan_by_id.return_value = loan
        uow.account.debit.side_effect = InsufficientFundsError()

        request = LoanRepaymentRequest(
            loan_id=10,
            amount=Decimal("500"),
        )

        with pytest.raises(InvalidRepaymentAmountError):
            await service.repay_loan(
                request,
                user_context,
            )

        assert loan.loan_amount == Decimal("1000")
        uow.transaction.add.assert_not_awaited()