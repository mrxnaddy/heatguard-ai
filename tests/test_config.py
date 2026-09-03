import pytest

from app.config import ConfigError, load_settings


def test_defaults_to_mock_mode(monkeypatch):
    monkeypatch.delenv("USE_MOCK_DATA", raising=False)
    monkeypatch.delenv("FORTYGUARD_API_KEY", raising=False)
    settings = load_settings()
    assert settings.use_mock_data is True
    assert settings.fortyguard_configured() is False


def test_real_mode_requires_api_key(monkeypatch):
    monkeypatch.setenv("USE_MOCK_DATA", "false")
    monkeypatch.delenv("FORTYGUARD_API_KEY", raising=False)
    with pytest.raises(ConfigError):
        load_settings()


def test_real_mode_with_api_key_is_valid(monkeypatch):
    monkeypatch.setenv("USE_MOCK_DATA", "false")
    monkeypatch.setenv("FORTYGUARD_API_KEY", "test-key-123")
    settings = load_settings()
    assert settings.use_mock_data is False
    assert settings.fortyguard_configured() is True


def test_cache_ttl_parsed_as_int(monkeypatch):
    monkeypatch.setenv("USE_MOCK_DATA", "true")
    monkeypatch.setenv("CACHE_TTL_SECONDS", "120")
    settings = load_settings()
    assert settings.cache_ttl_seconds == 120
