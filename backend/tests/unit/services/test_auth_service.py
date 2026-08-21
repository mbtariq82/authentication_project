from io import BytesIO

import pytest
from PIL import Image

from domain.user import User
from schemas.auth import RegisterCommand, TokenResponse
from services.auth_service import AuthService


class FakeUserRepository:
    def __init__(self) -> None:
        self.user: User | None = None

    async def get_by_email(self, email: str) -> User | None:
        if self.user and self.user.email == email:
            return self.user
        return None

    async def add(self, user: User) -> User:
        user.id = 7
        self.user = user
        return user

    async def save(self, user: User) -> User:
        self.user = user
        return user


class FakeRefreshTokenRepository:
    async def add(self, **kwargs) -> None:
        return None


class FakeAuthUnitOfWork:
    def __init__(self, fail_commit: bool = False) -> None:
        self.users = FakeUserRepository()
        self.refresh_tokens = FakeRefreshTokenRepository()
        self.fail_commit = fail_commit
        self.committed = False
        self.rolled_back = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type:
            self.rolled_back = True

    async def commit(self) -> None:
        if self.fail_commit:
            raise RuntimeError("commit failed")
        self.committed = True


class FakeProfileImageStorage:
    def __init__(self) -> None:
        self.saved: dict[str, bytes] = {}
        self.deleted: list[str] = []

    async def save(self, user_id: int, image: bytes) -> str:
        key = f"profile-images/{user_id}/avatar.webp"
        self.saved[key] = image
        return key

    async def delete(self, key: str) -> None:
        self.deleted.append(key)

    async def get_url(self, key: str) -> str:
        return f"https://images.example/{key}"


class FakeEventPublisher:
    def __init__(self) -> None:
        self.published: list[tuple[object, str]] = []

    async def publish(self, event: object, key: str) -> None:
        self.published.append((event, key))


def make_png() -> bytes:
    output = BytesIO()
    Image.new("RGB", (1600, 1200), color="blue").save(output, format="PNG")
    return output.getvalue()


def registration_command() -> RegisterCommand:
    return RegisterCommand(
        email="customer@example.com",
        first_name="Amina",
        last_name="Khan",
        password="SecureBank1!",
    )


def stub_token_issuance(service: AuthService) -> None:
    async def issue_tokens(user: User) -> TokenResponse:
        return TokenResponse(
            access_token="access-token",
            refresh_token="refresh-token",
        )

    service._issue_tokens = issue_tokens


@pytest.mark.asyncio
async def test_registration_stores_normalized_profile_image():
    uow = FakeAuthUnitOfWork()
    storage = FakeProfileImageStorage()
    service = AuthService(
        uow=uow,
        image_storage=storage,
        event_publisher=FakeEventPublisher(),
    )
    stub_token_issuance(service)

    response = await service.register(
        registration_command(),
        profile_image=make_png(),
    )

    assert response.access_token == "access-token"
    assert uow.committed is True
    assert uow.users.user is not None
    assert uow.users.user.profile_image_key == (
        "profile-images/7/avatar.webp"
    )

    stored_image = Image.open(
        BytesIO(storage.saved[uow.users.user.profile_image_key])
    )
    assert stored_image.format == "WEBP"
    assert stored_image.width <= 1024
    assert stored_image.height <= 1024


@pytest.mark.asyncio
async def test_registration_deletes_uploaded_image_if_commit_fails():
    uow = FakeAuthUnitOfWork(fail_commit=True)
    storage = FakeProfileImageStorage()
    service = AuthService(
        uow=uow,
        image_storage=storage,
        event_publisher=FakeEventPublisher(),
    )
    stub_token_issuance(service)

    with pytest.raises(RuntimeError, match="commit failed"):
        await service.register(
            registration_command(),
            profile_image=make_png(),
        )

    assert uow.rolled_back is True
    assert storage.deleted == ["profile-images/7/avatar.webp"]
