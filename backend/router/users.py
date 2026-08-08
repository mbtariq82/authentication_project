from fastapi import APIRouter, Depends#, HTTPException

from domain.user import User
from schemas.user import UserResponse
from dependencies.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def get_user_profile(
    user: User = Depends(get_current_user)
) -> UserResponse:
    return UserResponse.model_validate(user)
