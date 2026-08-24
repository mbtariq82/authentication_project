from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from rate_limiting.chat_rate_limiter import PublicChatRateLimiter


@pytest.mark.asyncio
async def test_public_chat_rate_limiter_sets_window_on_first_request():
    redis = AsyncMock()
    redis.incr.return_value = 1
    limiter = PublicChatRateLimiter(redis, max_requests=2, window_seconds=60)

    await limiter.check("127.0.0.1:guest-session")

    redis.expire.assert_awaited_once_with(
        "public_chat_rate_limit:127.0.0.1:guest-session",
        60,
    )


@pytest.mark.asyncio
async def test_public_chat_rate_limiter_rejects_requests_over_limit():
    redis = AsyncMock()
    redis.incr.return_value = 3
    redis.ttl.return_value = 42
    limiter = PublicChatRateLimiter(redis, max_requests=2)

    with pytest.raises(HTTPException) as exc_info:
        await limiter.check("127.0.0.1:guest-session")

    assert exc_info.value.status_code == 429
    assert exc_info.value.headers == {"Retry-After": "42"}