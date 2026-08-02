from fastapi import APIRouter, Depends#, HTTPException

from domain.user import User
from schemas import UserResponse, ConsultantPage
from services.consultant_service import ConsultantService
from dependencies import require_admin, get_consultant_service

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/dashboard", response_model=UserResponse)
async def get_admin_dashboard(
    admin: User = Depends(require_admin),
) -> UserResponse:
    return UserResponse.model_validate(admin)

@router.get("/consultants", response_model=ConsultantPage)
async def get_consultants(
    page: int = 1,
    page_size: int = 20,
    admin: User = Depends(require_admin),
    service: ConsultantService = Depends(get_consultant_service),
):
    return await service.list_consultants(
        page=page,
        page_size=page_size,
    )