from fastapi import APIRouter, Depends

from domain.user import User
from schemas import UserResponse, ConsultantPage, ListConsultantsQuery
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
    query: ListConsultantsQuery = Depends(),
    admin: User = Depends(require_admin),
    service: ConsultantService = Depends(get_consultant_service),
):
    return await service.list_consultants(query)