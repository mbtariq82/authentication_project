from redis.asyncio import Redis
from fastapi import HTTPException # ideally this should be replaced with custom handling

class LoginRateLimiter:
    def __init__(
        self,
        redis: Redis,
        max_attempts: int = 5,
        window_seconds: int = 60,
    ):
        self.redis = redis
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds

    async def check(self, identifier: str) -> None:
        key = f"login_rate_limit:{identifier}"

        attempts = await self.redis.incr(key)

        if attempts == 1:
            await self.redis.expire(
                key,
                self.window_seconds,
            )

        if attempts > self.max_attempts:
            retry_after = await self.redis.ttl(key)

            raise HTTPException(
                status_code=429,
                detail="Too many login attempts. Please try again later.",
                headers={
                    "Retry-After": str(max(retry_after, 1)),
                },
            )