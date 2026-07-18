from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User, RoleEnum
from schemas import UserResponse
from security import decode_token
from dependencies import get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
async def me(
    current_user: User = Depends(get_current_user)
) -> User:
    return current_user

@router.get("/admin", response_model=UserResponse)
async def admin(
    admin: User = Depends(require_admin),
) -> User:
    return admin
