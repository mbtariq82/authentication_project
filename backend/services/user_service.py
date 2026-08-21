import asyncio
import logging

from cache.abstract_user_cache import AbstractUserCache
from exceptions import InvalidAccessTokenError, InvalidProfileUpdateError
from profile_images import normalize_profile_image
from schemas.user import UpdateUserProfileCommand, UserResponse
from storage.abstract_profile_image_storage import AbstractProfileImageStorage
from unit_of_work.abstract_user_unit_of_work import AbstractUserUnitOfWork

logger = logging.getLogger(__name__)


class UserService:
    def __init__(
        self,
        cache: AbstractUserCache,
        uow: AbstractUserUnitOfWork,
        image_storage: AbstractProfileImageStorage,
    ) -> None:
        self.cache = cache
        self.uow = uow
        self.image_storage = image_storage

    async def get_by_id(
        self,
        user_id: int,
    ) -> UserResponse | None:
        cached_user = await self.cache.get_by_id(user_id)
        if cached_user:
            return UserResponse.model_validate(cached_user)

        async with self.uow:
            user = await self.uow.users.get_by_id(user_id)
        if not user:
            return None

        response = await self._to_response(user)
        await self._cache_response(response)
        return response

    async def update_profile(
        self,
        user_id: int,
        command: UpdateUserProfileCommand,
    ) -> UserResponse:
        if (
            command.first_name is None
            and command.last_name is None
            and command.profile_image is None
        ):
            raise InvalidProfileUpdateError("No profile changes were provided")

        new_image_key: str | None = None
        old_image_key: str | None = None

        try:
            async with self.uow:
                user = await self.uow.users.get_by_id(user_id)
                if user is None:
                    raise InvalidAccessTokenError()

                if command.first_name is not None:
                    user.first_name = self._normalize_name(
                        command.first_name,
                        "First name",
                    )
                if command.last_name is not None:
                    user.last_name = self._normalize_name(
                        command.last_name,
                        "Last name",
                    )

                if command.profile_image is not None:
                    normalized_image = await asyncio.to_thread(
                        normalize_profile_image,
                        command.profile_image,
                    )
                    old_image_key = user.profile_image_key
                    new_image_key = await self.image_storage.save(
                        user_id,
                        normalized_image,
                    )
                    user.profile_image_key = new_image_key

                user = await self.uow.users.save(user)
                await self.uow.commit()
        except Exception:
            if new_image_key is not None:
                await self._delete_image_safely(new_image_key)
            raise

        if old_image_key is not None and old_image_key != new_image_key:
            await self._delete_image_safely(old_image_key)

        response = await self._to_response(user)
        await self._cache_response(response)
        return response

    async def _to_response(self, user) -> UserResponse:
        profile_image_url = None
        if user.profile_image_key:
            profile_image_url = await self.image_storage.get_url(
                user.profile_image_key
            )
        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            profile_image_url=profile_image_url,
            phone=user.phone,
            address=user.address,
            dob=user.dob,
            postcode=user.postcode,
            country=user.country,
            city=user.city,
        )

    async def _cache_response(self, response: UserResponse) -> None:
        try:
            await self.cache.set(response)
        except Exception:
            logger.exception("Unable to cache user %s", response.id)

    async def _delete_image_safely(self, key: str) -> None:
        try:
            await self.image_storage.delete(key)
        except Exception:
            logger.exception("Unable to delete profile image %s", key)

    @staticmethod
    def _normalize_name(value: str, label: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise InvalidProfileUpdateError(f"{label} cannot be empty")
        if len(normalized) > 100:
            raise InvalidProfileUpdateError(
                f"{label} must be 100 characters or fewer"
            )
        return normalized
