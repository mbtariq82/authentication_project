from redis.asyncio import Redis


class LoginRateLimiter:
    def __init__(
        self,
        redis: Redis,
        maximum_attempts: int = 5,
        window_seconds: int = 60,
    ):
        self.redis = redis
        self.maximum_attempts = maximum_attempts
        self.window_seconds = window_seconds

    async def record_failed_attempt(self, identifier: str) -> int:
        key = self._build_key(identifier)

        attempts = await self.redis.incr(key)

        if attempts == 1:
            await self.redis.expire(
                key,
                self.window_seconds,
            )

        return attempts

    async def is_blocked(self, identifier: str) -> bool:
        key = self._build_key(identifier)

        attempts = await self.redis.get(key)

        if attempts is None:
            return False

        return int(attempts) >= self.maximum_attempts

    async def reset(self, identifier: str) -> None:
        await self.redis.delete(
            self._build_key(identifier),
        )

    @staticmethod
    def _build_key(identifier: str) -> str:
        return f"login_attempts:{identifier.lower()}"