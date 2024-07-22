from dataclasses import dataclass

import aioredis

from bot.config import REDIS_DB, REDIS_HOST, REDIS_PORT
from bot.utils import Singleton


@dataclass
class RedisService(metaclass=Singleton):
    redis: aioredis.Redis | None = None

    @classmethod
    async def create(cls) -> "RedisService":
        redis = await aioredis.from_url(
            f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
        )
        return cls(redis)

    async def get_currency_rate(self, currency):
        if self.redis is None:
            raise AttributeError("Redis client not initialize")

        rate = await self.redis.get(f"currency:{currency}")
        return float(rate) if rate else None
