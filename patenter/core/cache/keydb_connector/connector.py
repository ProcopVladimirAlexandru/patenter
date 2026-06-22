from contextlib import asynccontextmanager

import redis.asyncio as redis

from patenter.core.cache.base_connector.base_connector import BaseCacheConnector


class KeyDBConnector(BaseCacheConnector):
    def __init__(self, url: str, decode_responses: bool = True):
        self._url: str = url
        self._pool = redis.ConnectionPool.from_url(url, decode_responses=decode_responses)

    @asynccontextmanager
    async def _get_client(self) -> redis.Redis:
        try:
            client = redis.Redis.from_pool(self._pool)
            yield client
        finally:
            await client.aclose()

    async def set(self, key: str, value: Any) -> None:
        async with self._get_client() as client:
            await client.set(key, value)

    async def get(self, key: str) -> Any:
        async with self._get_client() as client:
            return await client.get(key)
