import pytest

from app.config import load_settings
from app.services.cache import TTLCache
from app.services.fortyguard_client import FortyGuardClient
from app.utils.errors import LocationNotFoundError


def _mock_settings(monkeypatch):
    monkeypatch.setenv("USE_MOCK_DATA", "true")
    monkeypatch.delenv("FORTYGUARD_API_KEY", raising=False)
    return load_settings()


def test_client_uses_mock_provider_by_default(monkeypatch):
    settings = _mock_settings(monkeypatch)
    client = FortyGuardClient(settings=settings, cache=TTLCache())
    assert client.using_mock_data is True
    assert client.health_check() is True


def test_client_returns_validated_reading(monkeypatch):
    settings = _mock_settings(monkeypatch)
    client = FortyGuardClient(settings=settings, cache=TTLCache())
    reading = client.get_temperature("isb-blue-area")
    assert reading.source == "mock"
    assert -90 <= reading.temperature_c <= 60


def test_client_caches_repeated_calls(monkeypatch):
    settings = _mock_settings(monkeypatch)
    cache = TTLCache(default_ttl_seconds=60)
    client = FortyGuardClient(settings=settings, cache=cache)
    client.get_temperature("isb-blue-area")
    assert cache.get("temp:isb-blue-area") is not None


def test_client_unknown_location_raises(monkeypatch):
    settings = _mock_settings(monkeypatch)
    client = FortyGuardClient(settings=settings, cache=TTLCache())
    with pytest.raises(LocationNotFoundError):
        client.get_temperature("nonexistent-location")


def test_get_all_locations_returns_full_mock_set(monkeypatch):
    settings = _mock_settings(monkeypatch)
    client = FortyGuardClient(settings=settings, cache=TTLCache())
    locations = client.get_all_locations()
    assert len(locations) >= 5
    assert all(loc.source == "mock" for loc in locations)
