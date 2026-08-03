from fastapi import APIRouter, Depends

from domain.user import User
from schemas import (
    UserResponse, ConsultantPage, ListConsultantsQuery, ConsultantResponse,
    RegisterConsultantCommand,
)
from services.consultant_service import ConsultantService
from dependencies import require_admin, get_consultant_service
from services.consultant_service import ConsultantService

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)

@router.get("/dashboard")
async def get_admin_dashboard() -> None:
    return
    # TODO: Query the actual data for the admin dashboard and return it in the response

@router.get("/consultants", response_model=ConsultantPage)
async def get_consultants(
    query: ListConsultantsQuery = Depends(),
    service: ConsultantService = Depends(get_consultant_service),
):
    return await service.list_consultants(query)

@router.get(
    "/users",
    response_model=list[UserResponse],
)
async def get_users(
    service: ConsultantService = Depends(get_consultant_service),
):
    return await service.list_unassigned_users()
    # TODO: when we add a "View All Users" page, we should change the naming here

@router.post(
    "/consultants/new",
    response_model=ConsultantResponse
)
async def create_consultant(
    request: RegisterConsultantCommand,
    service: ConsultantService = Depends(get_consultant_service),
):
    return await service.create_consultant(request)