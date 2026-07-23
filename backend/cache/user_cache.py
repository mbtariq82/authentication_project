from redis.asyncio import Redis
from schemas import UserResponse


class UserCache:
    def __init__(
        self,
        redis: Redis,
        ttl_seconds: int = 300,
    ) -> None:
        self.redis = redis
        self.ttl_seconds = ttl_seconds

    @staticmethod
    def _key(user_id: int) -> str:
        return f"user:{user_id}"

    async def get_by_id(
        self,
        user_id: int,
    ) -> UserResponse | None:
        cached_user = await self.redis.get(
            self._key(user_id)
        )
        if not cached_user:
            return None
        return UserResponse.model_validate_json(cached_user)

    async def set(
        self,
        user: UserResponse,
    ) -> None:
        await self.redis.set(
            self._key(user.id),
            user.model_dump_json(),
            ex=self.ttl_seconds,
        )