from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import User, RoleEnum
from schemas import UserResponse
from security import oauth2_scheme, decode_token

router = APIRouter(prefix="/users", tags=["users"])

async def get_current_user(
    access_token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_token(access_token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user = await db.execute(
        select(User).where(User.id == int(payload.get("sub")))
    )
    user = user.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    return current_user

@router.get("/me", response_model=UserResponse)
async def me(
    current_user: User = Depends(get_current_user),
):
    return current_user

@router.get("/admin-only")
async def admin_only(
    current_admin: User = Depends(get_current_admin),
):
    return {
        "message": "You have admin access",
        "username": current_admin.username,
    }
