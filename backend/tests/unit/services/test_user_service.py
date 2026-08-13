from io import BytesIO

import pytest
from PIL import Image

from domain.user import User
from enums import Role
from exceptions import InvalidProfileImageError, InvalidProfileUpdateError
from schemas.user import UpdateUserProfileCommand, UserResponse
from services.user_service import UserService


class FakeUserCache:
    def __init__(self) -> None:
        self.responses: dict[int, UserResponse] = {}

    async def get_by_id(self, user_id: int) -> UserResponse | None:
        return self.responses.get(user_id)

    async def set(self, user: UserResponse) -> None:
        self.responses[user.id] = user


class FakeUserRepository:
    def __init__(self, user: User) -> None:
        self.user = user

    async def get_by_id(self, user_id: int) -> User | None:
        if self.user.id == user_id:
            return self.user
        return None

    async def save(self, user: User) -> User:
        self.user = user
        return user


class FakeUserUnitOfWork:
    def __init__(self, user: User) -> None:
        self.users = FakeUserRepository(user)
        self.committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        return None

    async def commit(self) -> None:
        self.committed = True


class FakeProfileImageStorage:
    def __init__(self) -> None:
        self.saved: dict[str, bytes] = {}
        self.deleted: list[str] = []

    async def save(self, user_id: int, image: bytes) -> str:
        key = f"profile-images/{user_id}/new.webp"
        self.saved[key] = image
        return key

    async def delete(self, key: str) -> None:
        self.deleted.append(key)

    async def get_url(self, key: str) -> str:
        return f"https://images.example/{key}"


def make_user(**changes) -> User:
    values = {
        "id": 7,
        "email": "user@example.com",
        "first_name": "Old",
        "last_name": "Name",
        "role": Role.USER,
    }
    values.update(changes)
    return User(**values)


def make_png() -> bytes:
    output = BytesIO()
    Image.new("RGB", (1600, 1200), color="blue").save(output, format="PNG")
    return output.getvalue()


@pytest.mark.asyncio
async def test_update_profile_changes_names_and_stores_normalized_image():
    user = make_user()
    uow = FakeUserUnitOfWork(user)
    cache = FakeUserCache()
    storage = FakeProfileImageStorage()
    service = UserService(cache=cache, uow=uow, image_storage=storage)

    response = await service.update_profile(
        user_id=7,
        command=UpdateUserProfileCommand(
            first_name="  New  ",
            last_name="Person",
            profile_image=make_png(),
        ),
    )

    assert uow.committed is True
    assert user.first_name == "New"
    assert user.last_name == "Person"
    assert user.profile_image_key == "profile-images/7/new.webp"
    assert response.profile_image_url.endswith("profile-images/7/new.webp")
    assert cache.responses[7] == response

    stored_image = Image.open(BytesIO(storage.saved[user.profile_image_key]))
    assert stored_image.format == "WEBP"
    assert stored_image.width <= 1024
    assert stored_image.height <= 1024


@pytest.mark.asyncio
async def test_update_profile_replaces_the_previous_image():
    old_key = "profile-images/7/old.webp"
    user = make_user(profile_image_key=old_key)
    storage = FakeProfileImageStorage()
    service = UserService(
        cache=FakeUserCache(),
        uow=FakeUserUnitOfWork(user),
        image_storage=storage,
    )

    await service.update_profile(
        user_id=7,
        command=UpdateUserProfileCommand(profile_image=make_png()),
    )

    assert storage.deleted == [old_key]


@pytest.mark.asyncio
async def test_update_profile_rejects_an_invalid_image():
    service = UserService(
        cache=FakeUserCache(),
        uow=FakeUserUnitOfWork(make_user()),
        image_storage=FakeProfileImageStorage(),
    )

    with pytest.raises(InvalidProfileImageError):
        await service.update_profile(
            user_id=7,
            command=UpdateUserProfileCommand(profile_image=b"not an image"),
        )


@pytest.mark.asyncio
async def test_update_profile_requires_at_least_one_change():
    service = UserService(
        cache=FakeUserCache(),
        uow=FakeUserUnitOfWork(make_user()),
        image_storage=FakeProfileImageStorage(),
    )

    with pytest.raises(InvalidProfileUpdateError):
        await service.update_profile(
            user_id=7,
            command=UpdateUserProfileCommand(),
        )
