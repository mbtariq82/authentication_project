from typing import Literal
from decimal import Decimal
from pydantic import BaseModel, field_validator, Field


class LoanApplicationRequest(BaseModel):
    loan_type: Literal[
        "House",
        "Automobile",
        "Education",
        "Emergency Expense",
    ]
    loan_amount: Decimal
    monthly_income: Decimal
    monthly_expenses: Decimal
    duration: int

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, value: int) -> int:
        if value <= 0 or value % 6 != 0:
            raise ValueError(
                "Duration must be a positive number divisible by 6."
            )
        return value

class LoanApplicationResponse(BaseModel):
    eligible: bool
    status: str
    loan_id: int | None = None

class LoanDecisionRequest(BaseModel):
    status: Literal["ACCEPTED", "REJECTED"]

class LoanResponse(BaseModel):
    id: int
    loan_type: str
    loan_amount: Decimal
    duration: int
    interest: int
    emi: Decimal
    current_loan_status: str

class LoanListResponse(BaseModel):
    loans: list[LoanResponse]

class LoanRepaymentRequest(BaseModel):
    loan_id: int
    amount: Decimal = Field(gt=0)

class LoanRepaymentResponse(BaseModel):
    loan_id: int
    repayment_amount: Decimal
    remaining_amount: Decimal
    status: str