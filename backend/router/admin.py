from fastapi import APIRouter, Depends#, HTTPException

from models import User
from schemas import UserResponse
from dependencies import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/dashboard", response_model=UserResponse)
async def get_admin_dashboard(
    admin: User = Depends(require_admin),
) -> UserResponse:
    return UserResponse.model_validate(admin)