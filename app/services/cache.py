from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


@dataclass
class _Entry(Generic[T]):
    value: T
    expires_at: float


class TTLCache(Generic[T]):
    def __init__(self, default_ttl_seconds: int = 300) -> None:
        self._default_ttl = default_ttl_seconds
        self._store: dict[str, _Entry[T]] = {}

    def set(self, key: str, value: T, ttl_seconds: Optional[int] = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
        self._store[key] = _Entry(value=value, expires_at=time.monotonic() + ttl)

    def get(self, key: str) -> Optional[T]:
        """Return the cached value if present and not expired, else None."""
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.monotonic() >= entry.expires_at:
            return None  # Return None for expired, but keep in store for get_stale()
        return entry.value

    def get_stale(self, key: str) -> Optional[T]:
        """Return the cached value even if expired (or None if never cached)."""
        entry = self._store.get(key)
        return entry.value if entry is not None else None

    def clear(self) -> None:
        self._store.clear()

    def __len__(self) -> int:
        return len(self._store)