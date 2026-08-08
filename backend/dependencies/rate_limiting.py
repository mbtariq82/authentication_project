from fastapi import Depends, Request
from redis.asyncio import Redis

from dependencies.redis import get_redis
from rate_limiting.login_rate_limiter import LoginRateLimiter


def get_login_rate_limiter(
    redis: Redis = Depends(get_redis),
) -> LoginRateLimiter:
    return LoginRateLimiter(
        redis=redis,
        max_attempts=3,
        window_seconds=60,
    )


async def enforce_login_rate_limit(
    request: Request,
    rate_limiter: LoginRateLimiter = Depends(get_login_rate_limiter),
) -> None:
    client_ip = request.client.host if request.client else "unknown"
    await rate_limiter.check(client_ip)
