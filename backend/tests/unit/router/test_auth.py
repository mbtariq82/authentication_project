import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from dependencies.auth import get_auth_service
from exception_handlers import register_exception_handlers
from profile_images import MAX_PROFILE_IMAGE_BYTES
from router.auth import router
from schemas.auth import RegisterCommand, TokenResponse


class FakeAuthService:
    def __init__(self) -> None:
        self.command: RegisterCommand | None = None
        self.profile_image: bytes | None = None

    async def register(
        self,
        command: RegisterCommand,
        profile_image: bytes | None = None,
    ) -> TokenResponse:
        self.command = command
        self.profile_image = profile_image
        return TokenResponse(
            access_token="access-token",
            refresh_token="refresh-token",
        )


def make_app(service: FakeAuthService) -> FastAPI:
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(router)
    app.dependency_overrides[get_auth_service] = lambda: service
    return app


def registration_data() -> dict[str, str]:
    return {
        "email": "customer@example.com",
        "first_name": "Amina",
        "last_name": "Khan",
        "password": "SecureBank1!",
    }


@pytest.mark.asyncio
async def test_registration_still_accepts_json():
    service = FakeAuthService()
    transport = ASGITransport(app=make_app(service))

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/auth/register", json=registration_data())

    assert response.status_code == 200
    assert service.command is not None
    assert service.command.email == "customer@example.com"
    assert service.profile_image is None


@pytest.mark.asyncio
async def test_registration_accepts_multipart_profile_image():
    service = FakeAuthService()
    transport = ASGITransport(app=make_app(service))

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/register",
            data=registration_data(),
            files={"profile_image": ("avatar.png", b"image", "image/png")},
        )

    assert response.status_code == 200
    assert service.command is not None
    assert service.command.first_name == "Amina"
    assert service.profile_image == b"image"


@pytest.mark.asyncio
async def test_registration_rejects_profile_image_larger_than_five_mb():
    service = FakeAuthService()
    transport = ASGITransport(app=make_app(service))

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/register",
            data=registration_data(),
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


@pytest.mark.asyncio
async def test_multipart_registration_validates_customer_details():
    service = FakeAuthService()
    transport = ASGITransport(app=make_app(service))
    invalid_data = registration_data()
    invalid_data.pop("email")

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/register",
            data=invalid_data,
            files={"profile_image": ("avatar.png", b"image", "image/png")},
        )

    assert response.status_code == 422
    assert service.command is None
