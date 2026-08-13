from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from dependencies.auth import get_current_user
from dependencies.users import get_user_service
from exceptions import ProfileImageTooLargeError
from schemas.user import UpdateUserProfileCommand, UserResponse
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])
MAX_PROFILE_IMAGE_BYTES = 5 * 1024 * 1024


@router.get("/me", response_model=UserResponse)
async def get_user_profile(
    user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(user)


@router.patch("/me", response_model=UserResponse)
async def update_user_profile(
    first_name: Annotated[str | None, Form(max_length=100)] = None,
    last_name: Annotated[str | None, Form(max_length=100)] = None,
    profile_image: Annotated[UploadFile | None, File()] = None,
    user: UserResponse = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    image_bytes = None
    if profile_image is not None:
        try:
            image_bytes = await profile_image.read(
                MAX_PROFILE_IMAGE_BYTES + 1
            )
        finally:
            await profile_image.close()
        if len(image_bytes) > MAX_PROFILE_IMAGE_BYTES:
            raise ProfileImageTooLargeError()

    return await service.update_profile(
        user_id=user.id,
        command=UpdateUserProfileCommand(
            first_name=first_name,
            last_name=last_name,
            profile_image=image_bytes,
        ),
    )
