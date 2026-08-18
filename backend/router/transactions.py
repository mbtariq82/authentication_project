from fastapi import APIRouter, Depends

from dependencies.auth import get_current_user
from dependencies.transactions import get_transaction_service
from domain.user import User
from enums import Role
from exceptions import InvalidAccessTokenError
from schemas.transaction import (
    PaginatedResponse,
    TransactionCreate,
    TransactionFilter,
    TransactionLogResponse,
    TransactionResponse,
)
from services.transaction_service import TransactionService


router = APIRouter(prefix="/transactions", tags=["transactions"])


def current_user_id(user: User) -> int:
    if user.id is None:
        raise InvalidAccessTokenError()
    return user.id


@router.post("", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    command: TransactionCreate,
    user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
) -> TransactionResponse:
    return await service.create(current_user_id(user), command)


@router.get("", response_model=PaginatedResponse[TransactionResponse])
async def list_transactions(
    filters: TransactionFilter = Depends(),
    user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
) -> PaginatedResponse[TransactionResponse]:
    return await service.list_transactions(current_user_id(user), filters)


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
) -> TransactionResponse:
    return await service.get(current_user_id(user), transaction_id)


@router.post("/{transaction_id}/cancel", response_model=TransactionResponse)
async def cancel_transaction(
    transaction_id: int,
    user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
) -> TransactionResponse:
    return await service.cancel(current_user_id(user), transaction_id)


@router.get(
    "/{transaction_id}/logs",
    response_model=list[TransactionLogResponse],
)
async def list_transaction_logs(
    transaction_id: int,
    user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service),
) -> list[TransactionLogResponse]:
    return await service.logs(
        current_user_id(user),
        transaction_id,
        is_admin=user.role is Role.ADMIN,
    )