from __future__ import annotations

import time
from typing import Any, Optional


class CacheInterface:
    def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        raise NotImplementedError


class InMemoryTTLCache(CacheInterface):
    def __init__(self) -> None:
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        record = self._store.get(key)
        if not record:
            return None
        expires_at, value = record
        if time.time() >= expires_at:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._store[key] = (time.time() + max(0, ttl_seconds), value)


class RedisCache(CacheInterface):
    def __init__(self, host: str = "127.0.0.1", port: int = 6379, db: int = 0) -> None:
        try:
            import redis  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("Redis python package not installed. Install 'redis' or use InMemoryTTLCache.") from exc
        self._redis = redis.Redis(host=host, port=port, db=db)

    def get(self, key: str) -> Optional[Any]:
        raw = self._redis.get(key)
        if raw is None:
            return None
        try:
            import json
            return json.loads(raw)
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        import json
        self._redis.setex(key, ttl_seconds, json.dumps(value))


def get_cache(prefer_redis: bool = False) -> CacheInterface:
    if prefer_redis:
        try:
            return RedisCache()
        except RuntimeError:
            return InMemoryTTLCache()
    return InMemoryTTLCache()


