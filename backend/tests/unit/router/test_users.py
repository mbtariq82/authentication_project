import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from dependencies.auth import get_current_user
from dependencies.users import get_user_service
from enums import Role
from exception_handlers import register_exception_handlers
from router.users import MAX_PROFILE_IMAGE_BYTES, router
from schemas.user import UpdateUserProfileCommand, UserResponse

CURRENT_USER = UserResponse(
    id=7,
    email="user@example.com",
    first_name="Old",
    last_name="Name",
    role=Role.USER,
)


class FakeUserService:
    def __init__(self) -> None:
        self.command: UpdateUserProfileCommand | None = None

    async def update_profile(
        self,
        user_id: int,
        command: UpdateUserProfileCommand,
    ) -> UserResponse:
        assert user_id == CURRENT_USER.id
        self.command = command
        return CURRENT_USER.model_copy(
            update={
                "first_name": command.first_name or CURRENT_USER.first_name,
                "last_name": command.last_name or CURRENT_USER.last_name,
            }
        )


def make_app(service: FakeUserService) -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: CURRENT_USER
    app.dependency_overrides[get_user_service] = lambda: service
    return app


@pytest.mark.asyncio
async def test_update_profile_accepts_multipart_fields_and_image():
    service = FakeUserService()
    transport = ASGITransport(app=make_app(service))

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.patch(
            "/users/me",
            data={"first_name": "New", "last_name": "Person"},
            files={"profile_image": ("avatar.png", b"image", "image/png")},
        )

    assert response.status_code == 200
    assert response.json()["first_name"] == "New"
    assert service.command is not None
    assert service.command.profile_image == b"image"


@pytest.mark.asyncio
async def test_update_profile_rejects_images_larger_than_five_mb():
    service = FakeUserService()
    transport = ASGITransport(app=make_app(service))

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.patch(
            "/users/me",
            files={
                "profile_image": (
                    "avatar.png",
                    b"x" * (MAX_PROFILE_IMAGE_BYTES + 1),
                    "image/png",
                )
            },
        )

    assert response.status_code == 413
    assert service.command is None
