from __future__ import annotations

import time

from typing import (
    Optional,
    Dict
)

from dataclasses import dataclass
from threading import RLock


@dataclass
class Entry:
    value: str
    expire_at: Optional[float]


class InMemoryStorage:
    '''

    '''

    def __init__(self) -> None:
        self._data: Dict[str, Entry] = {}
        self._lock = RLock()

    def _now(self) -> float:
        return time.monotonic()

    def _is_expire_unlocked(self, e: Entry) -> bool:
        return e.expire_at is not None and self._now() >= e.expire_at

    def _get_unlocked(self, key: str) -> Optional[Entry]:
        e = self._data.get(key)
        if e is None:
            return None
        if self._is_expire_unlocked(e):
            self._data.pop(key, None)
            return None
        return e

    def set(self, key: str, value: str, ex_seconds: Optional[int] = None) -> None:
        if not key:
            raise ValueError('key is required')
        if ex_seconds is not None:
            if not isinstance(ex_seconds, int) or ex_seconds <= 0:
                raise ValueError('value is not an integer or out of range')
            expire_at = self._now() + ex_seconds
        else:
            expire_at = None
        with self._lock:
            self._data[key] = Entry(value=value, expire_at=expire_at)

    def get(self, key: str) -> Optional[str]:
        with self._lock:
            e = self._get_unlocked(key)
            return None if e is None else e.value

    def ttl(self, key: str) -> int:
        e = self._get_unlocked(key)
        if e is None:
            return -2
        if e.expire_at is None:
            return -1
        remaining = e.expire_at - self._now()
        if remaining <= 0:
            self._data.pop(key, None)
            return -2
        return  int(remaining)