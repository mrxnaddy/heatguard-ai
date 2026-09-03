import time

from app.services.cache import TTLCache


def test_set_and_get_returns_value():
    cache = TTLCache(default_ttl_seconds=60)
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"


def test_get_missing_key_returns_none():
    cache = TTLCache(default_ttl_seconds=60)
    assert cache.get("missing") is None


def test_expired_entry_returns_none_from_get():
    cache = TTLCache(default_ttl_seconds=0.05)
    cache.set("key1", "value1")
    time.sleep(0.1)
    assert cache.get("key1") is None


def test_stale_entry_still_available_via_get_stale():
    cache = TTLCache(default_ttl_seconds=0.05)
    cache.set("key1", "value1")
    time.sleep(0.1)
    assert cache.get("key1") is None  # expired for normal get
    assert cache.get_stale("key1") == "value1"  # still recoverable


def test_per_call_ttl_overrides_default():
    cache = TTLCache(default_ttl_seconds=60)
    cache.set("short-lived", "value", ttl_seconds=0.05)
    time.sleep(0.1)
    assert cache.get("short-lived") is None


def test_clear_empties_cache():
    cache = TTLCache(default_ttl_seconds=60)
    cache.set("a", 1)
    cache.set("b", 2)
    assert len(cache) == 2
    cache.clear()
    assert len(cache) == 0
