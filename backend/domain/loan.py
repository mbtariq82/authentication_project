from dataclasses import dataclass

@dataclass
class LoanApplication:
    loan_type: str
    loan_amount: int
    monthly_income: int
    monthly_expenses: int
    duration: int

def assess_loan(application: LoanApplication) -> bool:
    disposable_income = (
        application.monthly_income - application.monthly_expenses
    )

    if disposable_income <= 0:
        return False

    monthly_repayment = application.loan_amount / application.duration

    if monthly_repayment > disposable_income * 0.30:
        return False

    return True