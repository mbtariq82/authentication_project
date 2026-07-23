from fastapi import APIRouter, Depends#, HTTPException

from schemas import UserResponse
from dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def me(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    return current_user