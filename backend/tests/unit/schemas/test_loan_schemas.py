import pytest
from decimal import Decimal
from pydantic import ValidationError

from schemas.loan import *

class TestLoanApplicationRequest:

    def test_valid_request(self):
        request = LoanApplicationRequest(
            loan_type="House",
            loan_amount=Decimal("250000"),
            monthly_income=Decimal("5000"),
            monthly_expenses=Decimal("2000"),
            duration=24,
        )

        assert request.loan_type == "House"
        assert request.loan_amount == Decimal("250000")
        assert request.monthly_income == Decimal("5000")
        assert request.monthly_expenses == Decimal("2000")
        assert request.duration == 24

    def test_duration_must_be_positive(self):
        with pytest.raises(ValidationError):
            LoanApplicationRequest(
                loan_type="House",
                loan_amount=Decimal("250000"),
                monthly_income=Decimal("5000"),
                monthly_expenses=Decimal("2000"),
                duration=0,
            )

    def test_duration_must_be_divisible_by_six(self):
        with pytest.raises(ValidationError):
            LoanApplicationRequest(
                loan_type="House",
                loan_amount=Decimal("250000"),
                monthly_income=Decimal("5000"),
                monthly_expenses=Decimal("2000"),
                duration=7,
            )

    @pytest.mark.parametrize("duration", [6, 12, 18, 24, 30, 36])
    def test_valid_durations(self, duration):
        request = LoanApplicationRequest(
            loan_type="House",
            loan_amount=Decimal("250000"),
            monthly_income=Decimal("5000"),
            monthly_expenses=Decimal("2000"),
            duration=duration,
        )

        assert request.duration == duration

    @pytest.mark.parametrize(
        "loan_type",
        ["Invalid", "Personal", "Car", ""],
    )
    def test_invalid_loan_type(self, loan_type):
        with pytest.raises(ValidationError):
            LoanApplicationRequest(
                loan_type=loan_type,
                loan_amount=Decimal("250000"),
                monthly_income=Decimal("5000"),
                monthly_expenses=Decimal("2000"),
                duration=24,
            )

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            LoanApplicationRequest()


class TestLoanApplicationResponse:

    def test_valid_response(self):
        response = LoanApplicationResponse(
            eligible=True,
            status="ACCEPTED",
            loan_id=123,
        )

        assert response.eligible is True
        assert response.status == "ACCEPTED"
        assert response.loan_id == 123

    def test_loan_id_defaults_to_none(self):
        response = LoanApplicationResponse(
            eligible=False,
            status="REJECTED",
        )

        assert response.loan_id is None


class TestLoanDecisionRequest:

    @pytest.mark.parametrize("status", ["ACCEPTED", "REJECTED"])
    def test_valid_status(self, status):
        request = LoanDecisionRequest(status=status)

        assert request.status == status

    def test_invalid_status(self):
        with pytest.raises(ValidationError):
            LoanDecisionRequest(status="PENDING")


class TestLoanResponse:

    def test_valid_response(self):
        response = LoanResponse(
            id=1,
            loan_type="House",
            loan_amount=Decimal("250000"),
            duration=24,
            interest=5,
            emi=Decimal("10985.50"),
            current_loan_status="ACTIVE",
        )

        assert response.id == 1
        assert response.loan_type == "House"
        assert response.loan_amount == Decimal("250000")
        assert response.duration == 24
        assert response.interest == 5
        assert response.emi == Decimal("10985.50")
        assert response.current_loan_status == "ACTIVE"


class TestLoanListResponse:

    def test_valid_loan_list(self):
        loan = LoanResponse(
            id=1,
            loan_type="House",
            loan_amount=Decimal("250000"),
            duration=24,
            interest=5,
            emi=Decimal("10985.50"),
            current_loan_status="ACTIVE",
        )

        response = LoanListResponse(loans=[loan])

        assert len(response.loans) == 1
        assert response.loans[0].id == 1

    def test_empty_loan_list(self):
        response = LoanListResponse(loans=[])

        assert response.loans == []


class TestLoanRepaymentRequest:

    def test_valid_request(self):
        request = LoanRepaymentRequest(
            loan_id=1,
            amount=Decimal("500"),
        )

        assert request.loan_id == 1
        assert request.amount == Decimal("500")

    def test_amount_must_be_positive(self):
        with pytest.raises(ValidationError):
            LoanRepaymentRequest(
                loan_id=1,
                amount=Decimal("0"),
            )

    def test_negative_amount_is_invalid(self):
        with pytest.raises(ValidationError):
            LoanRepaymentRequest(
                loan_id=1,
                amount=Decimal("-100"),
            )


class TestLoanRepaymentResponse:

    def test_valid_response(self):
        response = LoanRepaymentResponse(
            loan_id=1,
            repayment_amount=Decimal("500"),
            remaining_amount=Decimal("4500"),
            status="PARTIALLY_PAID",
        )

        assert response.loan_id == 1
        assert response.repayment_amount == Decimal("500")
        assert response.remaining_amount == Decimal("4500")
        assert response.status == "PARTIALLY_PAID"