from typing import Annotated
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession


from sqlalchemy import select


from database import get_db
from dependencies import get_auth_service 
from models import RefreshToken, User
from schemas import TokenResponse, UserCreate, UserResponse, RefreshTokenRequest
from security import pwd_context, create_access_token, create_refresh_token, decode_token
from services.auth_service import AuthService
from dependencies import get_auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service)      
):
        return await service.login(
            form_data.username,
            form_data.password
        )

# we are not issuing refresh or access tokens during registration
@router.post("/register", response_model=UserResponse)
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    existing_user = await db.execute(
        select(User).where(User.username == user_create.username)
    )
    existing_user = existing_user.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=409, 
            detail="Username already registered"
        )
        
    new_user = User(
        username=user_create.username,
        hashed_password=pwd_context.hash(user_create.password),
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    payload = decode_token(request.token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    refresh_record = await db.execute(
        select(RefreshToken).where(RefreshToken.token == request.token)
    )
    refresh_record = refresh_record.scalar_one_or_none()

    if not refresh_record or refresh_record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired or revoked")

    user = (
        await db.execute(select(User).where(User.id == int(payload.get("sub"))))
    )
    user = user.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    new_access_token = create_access_token(subject=str(user.id))
    new_refresh_token, new_expire = create_refresh_token(subject=str(user.id))
    refresh_record.token = new_refresh_token
    refresh_record.expires_at = new_expire
    
    await db.commit()
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    refresh_record = await db.execute(
        select(RefreshToken).where(RefreshToken.token == request.token)
    )
    refresh_record = refresh_record.scalar_one_or_none()
    if refresh_record:
        await db.delete(refresh_record)
        await db.commit()