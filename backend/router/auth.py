from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from dependencies import get_auth_service 
from schemas import RegisterCommand, LoginCommand, LogoutCommand, RefreshCommand, TokenResponse
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse)
async def register(
    command: RegisterCommand,
    service: AuthService = Depends(get_auth_service)
):
    return await service.register(command)

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service)      
):
    login_command = LoginCommand(
        username=form_data.username,
        password=form_data.password
    )
    return await service.login(login_command)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    command: RefreshCommand,
    service: AuthService = Depends(get_auth_service)
):
    return await service.refresh(command)

@router.post("/logout")
async def logout(
    command: LogoutCommand,
    service: AuthService = Depends(get_auth_service)
):
    return await service.logout(command)