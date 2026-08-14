

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies.auth import require_admin
from dependencies.database import get_db
from schemas.admin_schema import UserStatusUpdate, UserResponse
from services.admin_service import AdminUserService

router = APIRouter(prefix="/admin", tags=["Admin"])
# , dependencies=[Depends(require_admin)]

@router.patch("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    data: UserStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = AdminUserService(db)

    return await service.update_status(
        user_id=user_id,
        new_status=data.status,
    )

@router.get("/all_users", response_model=list[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = AdminUserService(db)

    return await service.get_all_users(
        skip=skip,
        limit=limit,
    )