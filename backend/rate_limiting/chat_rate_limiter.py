from fastapi import HTTPException
from redis.asyncio import Redis


class PublicChatRateLimiter:
    def __init__(
        self,
        redis: Redis,
        max_requests: int = 10,
        window_seconds: int = 60,
    ):
        self.redis = redis
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def check(self, identifier: str) -> None:
        key = f"public_chat_rate_limit:{identifier}"
        requests = await self.redis.incr(key)

        if requests == 1:
            await self.redis.expire(key, self.window_seconds)

        if requests > self.max_requests:
            retry_after = await self.redis.ttl(key)
            raise HTTPException(
                status_code=429,
                detail="Too many chat requests. Please try again later.",
                headers={"Retry-After": str(max(retry_after, 1))},
            )