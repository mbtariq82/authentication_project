from fastapi import APIRouter, Depends
from schemas.loan import (LoanApplicationRequest, LoanApplicationResponse, LoanDecisionRequest, LoanListResponse, LoanRepaymentRequest, LoanRepaymentResponse)
from services.loan_service import LoanService
from unit_of_work.abstract_loan_unit_of_work import AbstractLoanUnitOfWork
from domain.card import AuthenticatedUserContext
from domain.user import User
from dependencies.auth import get_user_account, require_admin
from dependencies.loan import get_loan_service, get_loan_uow

router = APIRouter(prefix="/loans", tags=["Loans"])


@router.post("/loanForm", response_model=LoanApplicationResponse)
async def apply_for_loan(
    request: LoanApplicationRequest,
    user_context: AuthenticatedUserContext = Depends(get_user_account),
    loan_service: LoanService = Depends(get_loan_service)):
    return await loan_service.apply_for_loan(
        request=request,
        user_context=user_context)

@router.get("/pending", response_model=LoanListResponse)
async def get_pending_loans(
    admin: User = Depends(require_admin),
    loan_service: LoanService = Depends(get_loan_service),
):
    return await loan_service.get_pending_loans()

@router.patch("/{loan_id}/decision", response_model=LoanApplicationResponse)
async def decide_loan(
    loan_id: int,
    request: LoanDecisionRequest,
    admin: User = Depends(require_admin),
    loan_service: LoanService = Depends(get_loan_service),
):
    return await loan_service.update_loan_status(
        loan_id=loan_id,
        status=request.status)

@router.get("/my-loans", response_model=LoanListResponse)
async def get_my_loans(
    user_context: AuthenticatedUserContext = Depends(get_user_account),
    loan_service: LoanService = Depends(get_loan_service)
):
    return await loan_service.get_user_loans(user_context=user_context)

@router.post(
    "/repay",
    response_model=LoanRepaymentResponse,
)
async def repay_loan(
    request: LoanRepaymentRequest,
    user_context: AuthenticatedUserContext = Depends(get_user_account),
    loan_service: LoanService = Depends(get_loan_service),
):
    return await loan_service.repay_loan(
        request=request,
        user_context=user_context,
    )