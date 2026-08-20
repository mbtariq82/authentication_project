from decimal import Decimal
from dataclasses import dataclass

@dataclass
class LoanApplication:
    loan_type: str
    loan_amount: Decimal
    monthly_income: Decimal
    monthly_expenses: Decimal
    interest: int
    duration: int

def assess_loan(application: LoanApplication) -> bool:
    disposable_income = (
        application.monthly_income - application.monthly_expenses
    )

    if disposable_income <= 0:
        return False

    monthly_repayment = application.loan_amount / application.duration

    if monthly_repayment > disposable_income * Decimal("0.30"):
        return False

    return True

def get_interest_rate(loan_type: str) -> int:
    rates = {
        "House": 5,
        "Automobile": 6,
        "Education": 4,
        "Emergency Expense": 8,
    }

    return rates[loan_type]

def calculate_emi(loan_amount: Decimal, interest: int, duration: int) -> Decimal:
    monthly_rate = (
        Decimal(interest) / Decimal("100") / Decimal("12")
    )

    if monthly_rate == 0:
        return loan_amount / Decimal(duration)

    emi = (
        loan_amount
        * monthly_rate
        * (Decimal("1") + monthly_rate) ** duration
    ) / (
        (Decimal("1") + monthly_rate) ** duration
        - Decimal("1")
    )

    return emi.quantize(Decimal("0.01"))
