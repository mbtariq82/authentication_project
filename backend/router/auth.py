from json import JSONDecodeError

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from starlette.datastructures import UploadFile

from dependencies.auth import get_auth_service
from dependencies.rate_limiting import enforce_login_rate_limit
from profile_images import read_profile_image
from schemas.auth import (
    GoogleLoginCommand,
    LoginCommand,
    LogoutCommand,
    RefreshCommand,
    RegisterCommand,
    TokenResponse,
)
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
REGISTER_FIELDS = ("email", "first_name", "last_name", "password")
REGISTER_PROPERTIES = {
    "email": {"type": "string", "format": "email"},
    "first_name": {"type": "string", "maxLength": 100},
    "last_name": {"type": "string", "maxLength": 100},
    "password": {
        "type": "string",
        "format": "password",
        "minLength": 12,
        "maxLength": 72,
    },
}
REGISTER_REQUEST_BODY = {
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "required": list(REGISTER_FIELDS),
                    "properties": REGISTER_PROPERTIES,
                },
            },
            "multipart/form-data": {
                "schema": {
                    "type": "object",
                    "required": list(REGISTER_FIELDS),
                    "properties": {
                        **REGISTER_PROPERTIES,
                        "profile_image": {
                            "type": "string",
                            "format": "binary",
                        },
                    },
                },
            },
        },
    },
}


@router.post(
    "/register",
    response_model=TokenResponse,
    openapi_extra=REGISTER_REQUEST_BODY,
)
async def register(
    request: Request,
    service: AuthService = Depends(get_auth_service),
):
    command, profile_image = await _parse_registration_request(request)
    return await service.register(command, profile_image=profile_image)


async def _parse_registration_request(
    request: Request,
) -> tuple[RegisterCommand, bytes | None]:
    content_type = (
        request.headers.get("content-type", "")
        .partition(";")[0]
        .strip()
        .lower()
    )
    profile_image = None

    if content_type == "multipart/form-data":
        form = await request.form()
        payload = {
            field: form[field]
            for field in REGISTER_FIELDS
            if field in form
        }
        upload = form.get("profile_image")
        if upload is not None:
            if not isinstance(upload, UploadFile):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="profile_image must be a file",
                )
            if upload.filename:
                profile_image = await read_profile_image(upload)
            else:
                await upload.close()
    elif content_type in {"application/json", ""}:
        try:
            payload = await request.json()
        except (JSONDecodeError, UnicodeDecodeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Request body must be valid JSON",
            ) from exc
    else:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Use application/json or multipart/form-data",
        )

    try:
        command = RegisterCommand.model_validate(payload)
    except ValidationError as exc:
        raise RequestValidationError(exc.errors(), body=payload) from exc
    return command, profile_image

@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(enforce_login_rate_limit)],
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    login_command = LoginCommand(
        email=form_data.username,
        password=form_data.password,
    )
    return await service.login(login_command)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    command: RefreshCommand,
    service: AuthService = Depends(get_auth_service),
):
    return await service.refresh(command)

@router.post("/logout")
async def logout(
    command: LogoutCommand,
    service: AuthService = Depends(get_auth_service),
):
    return await service.logout(command)

@router.post("/google", response_model=TokenResponse)
async def google_login(
    command: GoogleLoginCommand,
    service: AuthService = Depends(get_auth_service),
):
    return await service.google_login(command)
