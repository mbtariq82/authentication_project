from decimal import Decimal

import pytest

from domain.loan import *


class TestLoanApplication:

    def test_creates_loan_application(self):
        application = LoanApplication(
            loan_type="House",
            loan_amount=Decimal("100000"),
            monthly_income=Decimal("5000"),
            monthly_expenses=Decimal("2000"),
            interest=5,
            duration=120,
        )

        assert application.loan_type == "House"
        assert application.loan_amount == Decimal("100000")
        assert application.monthly_income == Decimal("5000")
        assert application.monthly_expenses == Decimal("2000")
        assert application.interest == 5
        assert application.duration == 120


class TestAssessLoan:

    def test_loan_is_approved_when_affordable(self):
        application = LoanApplication(
            loan_type="House",
            loan_amount=Decimal("10000"),
            monthly_income=Decimal("5000"),
            monthly_expenses=Decimal("2000"),
            interest=5,
            duration=12,
        )

        assert assess_loan(application) is True

    def test_loan_is_rejected_when_disposable_income_is_zero(self):
        application = LoanApplication(
            loan_type="House",
            loan_amount=Decimal("10000"),
            monthly_income=Decimal("2000"),
            monthly_expenses=Decimal("2000"),
            interest=5,
            duration=12,
        )

        assert assess_loan(application) is False

    def test_loan_is_rejected_when_disposable_income_is_negative(self):
        application = LoanApplication(
            loan_type="House",
            loan_amount=Decimal("10000"),
            monthly_income=Decimal("2000"),
            monthly_expenses=Decimal("2500"),
            interest=5,
            duration=12,
        )

        assert assess_loan(application) is False

    def test_loan_is_rejected_when_repayment_exceeds_30_percent_of_disposable_income(self):
        application = LoanApplication(
            loan_type="House",
            loan_amount=Decimal("10000"),
            monthly_income=Decimal("3000"),
            monthly_expenses=Decimal("2000"),
            interest=5,
            duration=10,
        )

        # Disposable income = 1000
        # Maximum repayment = 1000 * 0.30 = 300
        # Monthly repayment = 10000 / 10 = 1000
        assert assess_loan(application) is False

    def test_loan_is_approved_when_repayment_is_exactly_30_percent(self):
        application = LoanApplication(
            loan_type="House",
            loan_amount=Decimal("3000"),
            monthly_income=Decimal("2000"),
            monthly_expenses=Decimal("1000"),
            interest=5,
            duration=10,
        )

        # Disposable income = 1000
        # 30% = 300
        # Monthly repayment = 300
        assert assess_loan(application) is True


class TestGetInterestRate:

    @pytest.mark.parametrize(
        "loan_type, expected_rate",
        [
            ("House", 5),
            ("Automobile", 6),
            ("Education", 4),
            ("Emergency Expense", 8),
        ],
    )
    def test_returns_correct_interest_rate(self, loan_type, expected_rate):
        assert get_interest_rate(loan_type) == expected_rate

    def test_invalid_loan_type_raises_key_error(self):
        with pytest.raises(KeyError):
            get_interest_rate("Invalid Loan")


class TestCalculateEmi:

    def test_calculates_emi(self):
        emi = calculate_emi(
            loan_amount=Decimal("10000"),
            interest=12,
            duration=12,
        )

        assert emi == Decimal("888.49")

    def test_zero_interest(self):
        emi = calculate_emi(
            loan_amount=Decimal("12000"),
            interest=0,
            duration=12,
        )

        assert emi == Decimal("1000")

    def test_zero_interest_with_decimal_amount(self):
        emi = calculate_emi(
            loan_amount=Decimal("10000"),
            interest=0,
            duration=4,
        )

        assert emi == Decimal("2500")

    def test_emi_is_rounded_to_two_decimal_places(self):
        emi = calculate_emi(
            loan_amount=Decimal("1000"),
            interest=5,
            duration=12,
        )

        assert emi.as_tuple().exponent == -2

    def test_larger_loan(self):
        emi = calculate_emi(
            loan_amount=Decimal("250000"),
            interest=5,
            duration=120,
        )

        assert emi > Decimal("0")
        assert emi == Decimal("2651.64")