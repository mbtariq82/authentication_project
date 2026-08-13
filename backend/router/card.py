from fastapi import APIRouter, Depends

from dependencies.card import get_card_service
from dependencies.auth import get_current_user, get_user_account
from domain.user import User
from domain.card import AuthenticatedUserContext
from schemas.card import CardResponse, CardDetailsResponse, CardDetailsRequest
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



