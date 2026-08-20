from fastapi import APIRouter, Depends

from dependencies.accounts import get_account_service
from dependencies.auth import get_current_user
from domain.user import User
from schemas.account import AccountResponse, CloseAccountRequest
from services.account_service import AccountService



router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.get("/me", response_model=AccountResponse)
async def get_account(
    user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> AccountResponse:
    return await service.get_account(user.id)

@router.patch("/me/freeze", response_model=AccountResponse)
async def freeze_account(
    user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> AccountResponse:
    return await service.freeze_account(user.id)


@router.patch("/me/unfreeze", response_model=AccountResponse)
async def unfreeze_account(
    user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> AccountResponse:
    return await service.unfreeze_account(user.id)


@router.patch("/me/close", response_model=AccountResponse)
async def close_account(
    data: CloseAccountRequest,
    user: User = Depends(get_current_user),
    service: AccountService = Depends(get_account_service),
) -> AccountResponse:
    return await service.close_account(user.id, data.close_reason)