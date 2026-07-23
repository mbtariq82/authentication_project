from cache.user_cache import UserCache
from repositories.user_repository import UserRepository
from schemas import UserResponse


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        user_cache: UserCache,
    ):
        self.user_repository = user_repository
        self.user_cache = user_cache

    async def get_by_id(
        self,
        user_id: int,
    ) -> UserResponse | None:
        cached_user = await self.user_cache.get_by_id(user_id)
        if cached_user:
            return UserResponse.model_validate(cached_user)
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None
        response = UserResponse.model_validate(user)
        await self.user_cache.set(response) # set UserResponse, not User
        return response