

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies.card import get_card_service
from dependencies.auth import require_admin
from dependencies.database import get_db
from schemas.admin_schema import UpdateUserStatusCommand, AdminUserResponse,UpdateAccountStatus, UpdateCardStatus
from services.admin_service import AdminUserService, AdminCardService, AdminAccountService
from services.card_service import CardService
from schemas.card import AdminCardResponse
from schemas.account import AdminAccountResponse

router = APIRouter(
    prefix="/admin", 
    tags=["Admin"],
    dependencies=[Depends(require_admin)]
)

@router.patch("/users/status")
async def update_user_status(
    data: UpdateUserStatusCommand,
    db: AsyncSession = Depends(get_db),card_service: CardService = Depends(get_card_service),
):
    service = AdminUserService(db, card_service=card_service,)

    return await service.update_status(
        user_id=data.user_id,
        new_status=data.status,
        rejection_reason=data.rejection_reason,
    )


@router.get("/all_users", response_model=list[AdminUserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),card_service: CardService = Depends(get_card_service),
):
    service = AdminUserService(db, card_service=card_service,)

    return await service.list_users(
        skip=skip,
        limit=limit,
    )

@router.get("/all_accounts", response_model=list[AdminAccountResponse])
async def get_all_accounts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = AdminAccountService(db)

    return await service.list_accounts(
        skip=skip,
        limit=limit,
    )



#     )
@router.patch("/account/status")
async def update_account_status(
    data: UpdateAccountStatus,
    db: AsyncSession = Depends(get_db),
):
    admin_card_service = AdminCardService(db)

    service = AdminAccountService(
        db,
        card_service=admin_card_service,
    )

    return await service.update_status(
        account_id=data.account_id,
        account_status=data.account_status,
        close_reason=data.close_reason,
    )

@router.get("/all_cards", response_model=list[AdminCardResponse])
async def get_all_cards(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = AdminCardService(db)

    return await service.list_cards(
        skip=skip,
        limit=limit,
    )


@router.patch("/card/status")
async def update_card_status(
    data: UpdateCardStatus,
    db: AsyncSession = Depends(get_db),
):
    service = AdminCardService(db)

    return await service.update_status(
        card_id=data.card_id,
        new_status=data.status,
        reason=data.reason,
    )