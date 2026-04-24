import os
from typing import Optional, Dict, Any
import time


class SessionCache:
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None

        entry = self.cache[key]
        if time.time() - entry['timestamp'] > self.ttl:
            del self.cache[key]
            return None

        return entry['value']

    def set(self, key: str, value: Any):
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]

        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }

    def delete(self, key: str):
        if key in self.cache:
            del self.cache[key]

    def clear_expired(self):
        current_time = time.time()
        expired_keys = [
            k for k, v in self.cache.items()
            if current_time - v['timestamp'] > self.ttl
        ]
        for key in expired_keys:
            del self.cache[key]


_cache = None


def get_session_cache() -> SessionCache:
    global _cache
    if _cache is None:
        _cache = SessionCache()
    return _cache
