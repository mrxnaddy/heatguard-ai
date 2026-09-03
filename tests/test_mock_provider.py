import pytest

from app.services.fortyguard_client import MockProvider
from app.utils.errors import LocationNotFoundError


def test_mock_provider_health_check_always_true():
    provider = MockProvider()
    assert provider.health_check() is True


def test_mock_provider_returns_labeled_mock_data():
    provider = MockProvider()
    readings = provider.get_all()
    assert len(readings) > 0
    for reading in readings:
        assert reading.source == "mock"
        assert reading.confidence in {"high", "partial", "low"}


def test_mock_provider_get_temperature_known_location():
    provider = MockProvider()
    reading = provider.get_temperature("isb-blue-area")
    assert reading.location_id == "isb-blue-area"
    assert reading.source == "mock"


def test_mock_provider_unknown_location_raises():
    provider = MockProvider()
    with pytest.raises(LocationNotFoundError):
        provider.get_temperature("does-not-exist")


def test_mock_provider_bulk_matches_individual_calls():
    provider = MockProvider()
    ids = ["isb-blue-area", "rwp-saddar"]
    bulk = provider.get_temperatures_bulk(ids)
    assert [r.location_id for r in bulk] == ids
