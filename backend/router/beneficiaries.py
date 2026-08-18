from fastapi import APIRouter, Depends, Query

from dependencies.auth import get_current_user
from dependencies.beneficiaries import get_beneficiary_service
from domain.user import User
from schemas.beneficiary import (
    BeneficiaryCreate,
    BeneficiaryResponse,
    BeneficiaryUpdate,
)
from services.beneficiary_service import BeneficiaryService


router = APIRouter(prefix="/beneficiaries", tags=["beneficiaries"])


@router.post("", response_model=BeneficiaryResponse, status_code=201)
async def create_beneficiary(
    command: BeneficiaryCreate,
    user: User = Depends(get_current_user),
    service: BeneficiaryService = Depends(get_beneficiary_service),
) -> BeneficiaryResponse:
    return await service.create(user.id, command)


@router.get("", response_model=list[BeneficiaryResponse])
async def list_beneficiaries(
    include_inactive: bool = Query(default=False),
    user: User = Depends(get_current_user),
    service: BeneficiaryService = Depends(get_beneficiary_service),
) -> list[BeneficiaryResponse]:
    return await service.list(
        user.id,
        include_inactive=include_inactive,
    )


@router.get("/{beneficiary_id}", response_model=BeneficiaryResponse)
async def get_beneficiary(
    beneficiary_id: int,
    include_inactive: bool = Query(default=False),
    user: User = Depends(get_current_user),
    service: BeneficiaryService = Depends(get_beneficiary_service),
) -> BeneficiaryResponse:
    return await service.get(
        user.id,
        beneficiary_id,
        include_inactive=include_inactive,
    )


@router.patch("/{beneficiary_id}", response_model=BeneficiaryResponse)
async def update_beneficiary(
    beneficiary_id: int,
    command: BeneficiaryUpdate,
    user: User = Depends(get_current_user),
    service: BeneficiaryService = Depends(get_beneficiary_service),
) -> BeneficiaryResponse:
    return await service.update(user.id, beneficiary_id, command)


@router.delete("/{beneficiary_id}", response_model=BeneficiaryResponse)
async def deactivate_beneficiary(
    beneficiary_id: int,
    user: User = Depends(get_current_user),
    service: BeneficiaryService = Depends(get_beneficiary_service),
) -> BeneficiaryResponse:
    return await service.deactivate(user.id, beneficiary_id)