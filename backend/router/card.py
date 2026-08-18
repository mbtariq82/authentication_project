from fastapi import APIRouter, Depends

from dependencies.card import get_card_service
from dependencies.auth import get_user_account, require_admin
from domain.user import User
from domain.card import AuthenticatedUserContext
from schemas.card import CardResponse, CardDetailsResponse, CardDetailsRequest, CardStatusResponse
from services.card_service import CardService

router = APIRouter(prefix="/cards", tags=["cards"])

@router.post("/details", response_model=CardDetailsResponse)
async def get_unmasked_card(request: CardDetailsRequest, context: AuthenticatedUserContext = Depends(get_user_account), service: CardService = Depends(get_card_service)):
    return await service.get_unmasked_card(
        account_id=context.account.id,
        email = context.user.email,
        password=request.password
    )

@router.get("", response_model=CardDetailsResponse)
async def get_user_card(context: AuthenticatedUserContext = Depends(get_user_account),
                        service: CardService = Depends(get_card_service)):
    return await service.get_user_card(
        account_id=context.account.id,
        user_id=context.user.id
    )

@router.post("", response_model=CardResponse)
async def create_card(context: AuthenticatedUserContext = Depends(get_user_account), 
                      service: CardService = Depends(get_card_service)
                      ):
    return await service.create_card(
        account_id=context.account.id,
        user_id = context.user.id
    )

@router.patch("/freeze", response_model=CardStatusResponse)
async def freeze_card(
    context: AuthenticatedUserContext = Depends(get_user_account),
    service: CardService = Depends(get_card_service)
):
    return await service.toggle_card_status(
        account_id = context.account.id,
        user_id = context.user.id
    )

# TODO: move this into /admin router
@router.patch("/block/{card_id}", response_model=CardStatusResponse)
async def block_card(
    card_id: int,
    current_user: User = Depends(require_admin),
    service: CardService = Depends(get_card_service)
):
    return await service.block_card(card_id)


