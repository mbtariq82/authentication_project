import math
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4
from domain.loan import (
    LoanApplication,
    assess_loan,
    get_interest_rate,
    calculate_emi,
    calculate_accrued_interest
)
from domain.transaction import Transaction
from enums import TransactionType, TransactionDirection, TransactionStatus
from domain.card import AuthenticatedUserContext
from models.loan import LoanRow
from schemas.loan import (
    LoanApplicationRequest,
    LoanApplicationResponse,
    LoanResponse,
    LoanListResponse,
    LoanRepaymentRequest,
    LoanRepaymentResponse,
)
from unit_of_work.abstract_loan_unit_of_work import AbstractLoanUnitOfWork
from exceptions import (
    LoanNotFoundError,
    InvalidLoanStatusError,
    PermissionDeniedError,
    InvalidRepaymentAmountError,
    InsufficientFundsError,
)


class LoanService:

    def __init__(self, uow: AbstractLoanUnitOfWork):
        self.uow = uow

    async def apply_for_loan(
        self,
        request: LoanApplicationRequest,
        user_context: AuthenticatedUserContext,
    ) -> LoanApplicationResponse:

        account_id = user_context.account.id

        interest = get_interest_rate(request.loan_type)

        application = LoanApplication(
            loan_type=request.loan_type,
            loan_amount=request.loan_amount,
            monthly_income=request.monthly_income,
            monthly_expenses=request.monthly_expenses,
            interest=interest,
            duration=request.duration,
        )

        eligible = assess_loan(application)

        if not eligible:
            return LoanApplicationResponse(
                eligible=False,
                status="REJECTED",
                loan_id=None,
            )

        emi = calculate_emi(
            loan_amount=request.loan_amount,
            interest=interest,
            duration=request.duration,
        )

        loan = LoanRow(
            account_id=account_id,
            loan_amount=request.loan_amount,
            duration=request.duration,
            current_loan_status="PENDING",
            loan_type=request.loan_type,
            interest=interest,
            emi=emi,
        )

        created_loan = await self.uow.loans.create(loan)

        return LoanApplicationResponse(
            eligible=True,
            status="PENDING",
            loan_id=created_loan.id,
        )

    async def update_loan_status(
        self,
        loan_id: int,
        status: str,
    ) -> LoanApplicationResponse:

        loan = await self.uow.loans.get_loan_by_id(loan_id)

        if not loan:
            raise LoanNotFoundError()

        if loan.current_loan_status != "PENDING":
            raise InvalidLoanStatusError()

        loan.current_loan_status = status
        
        if status == "ACCEPTED":
            loan.last_interest_calculated_at = datetime.now(timezone.utc)

        return LoanApplicationResponse(
            eligible=True,
            status=status,
            loan_id=loan.id,
        )

    def _get_accrued_interest(self, loan: LoanRow) -> Decimal:
            if (
                loan.current_loan_status != "ACCEPTED"
                or loan.last_interest_calculated_at is None
            ):
                return Decimal("0.00")
    
            now = datetime.now(timezone.utc)
    
            days_elapsed = (
                now.date() - loan.last_interest_calculated_at.date()
            ).days
    
            if days_elapsed <= 0:
                return Decimal("0.00")
    
            return calculate_accrued_interest(
                loan_amount=loan.loan_amount,
                interest=loan.interest,
                days_elapsed=days_elapsed,
            )

    async def get_user_loans(
        self,
        user_context: AuthenticatedUserContext,
    ) -> LoanListResponse:

        account_id = user_context.account.id

        loans = await self.uow.loans.get_loans_by_account_id(
            account_id=account_id
        )

        return LoanListResponse(
            loans=[
                LoanResponse(
                            id=loan.id,
                            loan_type=loan.loan_type,
                            loan_amount=loan.loan_amount,
                            duration=loan.duration,
                            interest=loan.interest,
                            emi=loan.emi,
                            current_loan_status=loan.current_loan_status,
                            accrued_interest=calculate_accrued_interest(
                                loan_amount=loan.loan_amount,
                                interest=loan.interest,
                                days_elapsed=(
                                    datetime.now(timezone.utc).date()
                                    - loan.last_interest_calculated_at.date()
                                ).days,
                            ),
                        )
                for loan in loans
            ]
        )

    async def get_pending_loans(self) -> LoanListResponse:

        loans = await self.uow.loans.get_pending_loans()

        return LoanListResponse(
            loans=[
                LoanResponse(
                            id=loan.id,
                            loan_type=loan.loan_type,
                            loan_amount=loan.loan_amount,
                            duration=loan.duration,
                            interest=loan.interest,
                            emi=loan.emi,
                            current_loan_status=loan.current_loan_status,
                        )
                for loan in loans
            ]
        )

    def calculate_duration(
        self,
        loan_amount: Decimal,
        interest: int,
        emi: Decimal,
    ) -> int:
        monthly_rate = (
            Decimal(interest) / Decimal("100") / Decimal("12")
        )

        if monthly_rate == 0:
            return math.ceil(loan_amount / emi)

        duration = (
            -math.log(
                1 - (
                    float(loan_amount * monthly_rate / emi)
                )
            )
            / math.log(1 + float(monthly_rate))
        )

        return math.ceil(duration)

    async def _accrue_interest(self, loan: LoanRow) -> None:
        now = datetime.now(timezone.utc)

        if loan.last_interest_calculated_at is None:
            loan.last_interest_calculated_at = now
            return

        last_date = loan.last_interest_calculated_at.date()
        current_date = now.date()

        days_elapsed = (current_date - last_date).days

        if days_elapsed <= 0:
            return

        accrued_interest = calculate_accrued_interest(
            loan_amount=loan.loan_amount,
            interest=loan.interest,
            days_elapsed=days_elapsed,
        )

        loan.loan_amount += accrued_interest
        loan.last_interest_calculated_at = now

    async def repay_loan(
        self,
        request: LoanRepaymentRequest,
        user_context: AuthenticatedUserContext,
    ) -> LoanRepaymentResponse:

        loan = await self.uow.loans.get_loan_by_id(request.loan_id)

        if not loan:
            raise LoanNotFoundError()

        if loan.account_id != user_context.account.id:
            raise PermissionDeniedError()

        if loan.current_loan_status != "ACCEPTED":
            raise InvalidLoanStatusError()

        await self._accrue_interest(loan)

        if request.amount > loan.loan_amount:
            raise InvalidRepaymentAmountError()

        try:
            await self.uow.account.debit(
                account_id=user_context.account.id,
                amount=request.amount,
            )
        except InsufficientFundsError:
            raise InvalidRepaymentAmountError()

        loan.loan_amount -= request.amount

        if loan.loan_amount == 0:
            loan.current_loan_status = "PAID"
            loan.duration = 0

        else:
            loan.duration = self.calculate_duration(
                loan_amount=loan.loan_amount,
                interest=loan.interest,
                emi=loan.emi,
            )

        transaction = Transaction(
            account_id=user_context.account.id,
            transaction_type=TransactionType.WITHDRAWAL,
            direction=TransactionDirection.DEBIT,
            amount=request.amount,
            reference=f"LOAN-{loan.id}-{uuid4().hex}",
            status=TransactionStatus.COMPLETED,
            description=f"Loan repayment for loan {loan.id}",
        )

        await self.uow.transaction.add(transaction)

        return LoanRepaymentResponse(
            loan_id=loan.id,
            repayment_amount=request.amount,
            remaining_amount=loan.loan_amount,
            status=loan.current_loan_status,
        )