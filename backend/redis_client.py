from redis.asyncio import Redis

from config import REDIS_URL

redis_client = Redis.from_url(
    REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
)