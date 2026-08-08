from schemas.user import UserResponse

from cache.abstract_user_cache import AbstractUserCache
from repositories.abstract_user_repository import AbstractUserRepository

class UserService:
    def __init__(
        self, 
        cache: AbstractUserCache,
        repository: AbstractUserRepository
    ):
        self.cache = cache
        self.repository = repository

    async def get_by_id(
        self,
        user_id: int,
    ) -> UserResponse | None:
        cached_user = await self.cache.get_by_id(user_id)
        if cached_user:
            return UserResponse.model_validate(cached_user)
        user = await self.repository.get_by_id(user_id)
        if not user:
            return None
        response = UserResponse.model_validate(user)
        await self.cache.set(response)
        return response
