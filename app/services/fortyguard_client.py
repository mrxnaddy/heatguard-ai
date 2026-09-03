"""
FortyGuard API adapter.
"""
from __future__ import annotations

import logging
import time
from typing import Protocol

import requests

from app.config import Settings, settings as default_settings
from app.data.mock_data import get_mock_reading, get_mock_readings
from app.data.models import TemperatureReading
from app.services.cache import TTLCache
from app.utils.errors import APIConnectionError, InvalidResponseError, LocationNotFoundError

logger = logging.getLogger("heatguard.fortyguard_client")


class TemperatureProvider(Protocol):
    def get_temperature(self, location_id: str) -> TemperatureReading: ...

    def get_temperatures_bulk(self, location_ids: list[str]) -> list[TemperatureReading]:
        ...

    def health_check(self) -> bool: ...


class MockProvider:
    def get_temperature(self, location_id: str) -> TemperatureReading:
        mapping = {
            "isb-blue-area": "blue-area",
            "isb-i9-industrial": "i9-industrial",
            "rwp-committee-chowk": "committee-chowk",
        }
        lookup_id = mapping.get(location_id, location_id)
        reading = get_mock_reading(lookup_id)
        if reading is not None:
            return reading

        cleaned = location_id.lower().strip()
        for r in get_mock_readings():
            if cleaned in r.location_id.lower() or r.location_id.lower() in cleaned:
                return r

        raise LocationNotFoundError(f"Unknown mock location_id: {location_id}")

    def get_temperatures_bulk(self, location_ids: list[str]) -> list[TemperatureReading]:
        return [self.get_temperature(loc_id) for loc_id in location_ids]

    def health_check(self) -> bool:
        return True

    def get_all(self) -> list[TemperatureReading]:
        return get_mock_readings()


class RealFortyGuardProvider:
    _MAX_RETRIES = 3
    _BACKOFF_BASE_SECONDS = 0.5

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._session = requests.Session()

    def _request_with_retry(self, method: str, path: str, **kwargs) -> requests.Response:
        last_exc: Exception | None = None
        for attempt in range(1, self._MAX_RETRIES + 1):
            try:
                url = f"{self._settings.fortyguard_base_url.rstrip('/')}/{path.lstrip('/')}"
                response = self._session.request(method, url, timeout=5, **kwargs)
                if response.status_code == 429:
                    wait = self._BACKOFF_BASE_SECONDS * (2 ** (attempt - 1))
                    time.sleep(wait)
                    continue
                response.raise_for_status()
                return response
            except requests.RequestException as exc:
                last_exc = exc
                wait = self._BACKOFF_BASE_SECONDS * (2 ** (attempt - 1))
                time.sleep(wait)
        raise APIConnectionError(str(last_exc) if last_exc else "FortyGuard request failed")

    def get_temperature(self, location_id: str) -> TemperatureReading:
        raise NotImplementedError("Real FortyGuard integration is not yet wired up.")

    def get_temperatures_bulk(self, location_ids: list[str]) -> list[TemperatureReading]:
        raise NotImplementedError("Real FortyGuard integration is not yet wired up.")

    def health_check(self) -> bool:
        if not self._settings.fortyguard_api_key:
            return False
        try:
            self._request_with_retry("GET", "health")
            return True
        except APIConnectionError:
            return False


class FortyGuardClient:
    def __init__(self, settings: Settings | None = None, cache: TTLCache | None = None) -> None:
        self._settings = settings or default_settings
        self._cache = cache if cache is not None else TTLCache(default_ttl_seconds=self._settings.cache_ttl_seconds)
        self._provider: TemperatureProvider = (
            MockProvider() if self._settings.use_mock_data else RealFortyGuardProvider(self._settings)
        )

    @property
    def using_mock_data(self) -> bool:
        return self._settings.use_mock_data

    def get_temperature(self, location_id: str) -> TemperatureReading:
        cache_key = f"temp:{location_id}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            reading = self._validate(self._provider.get_temperature(location_id))
            self._cache.set(cache_key, reading)
            return reading
        except APIConnectionError:
            stale = self._cache.get_stale(cache_key)
            if stale is not None:
                return stale
            raise

    def get_temperatures_bulk(self, location_ids: list[str]) -> list[TemperatureReading]:
        cache_key = "temps_bulk:" + ",".join(sorted(location_ids))
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            readings = [self._validate(self._provider.get_temperature(loc_id)) for loc_id in location_ids]
            self._cache.set(cache_key, readings)
            return readings
        except APIConnectionError:
            stale = self._cache.get_stale(cache_key)
            if stale is not None:
                return stale
            raise

    def get_all_locations(self) -> list[TemperatureReading]:
        if isinstance(self._provider, MockProvider):
            return self._provider.get_all()
        raise NotImplementedError

    def health_check(self) -> bool:
        return self._provider.health_call() if hasattr(self._provider, "health_call") else self._provider.health_check()

    @staticmethod
    def _validate(reading: TemperatureReading) -> TemperatureReading:
        if reading.temperature_c is None:
            raise InvalidResponseError("Missing temperature_c in provider response")
        return reading

    def get_live_weather(self, city_name: str) -> dict:
        import requests
        from app.config import settings
        
        short_forms = {
            "isb": "Islamabad",
            "lhr": "Lahore",
            "khi": "Karachi",
            "rwp": "Rawalpindi",
            "fsd": "Faisalabad",
            "mul": "Multan",
            "pew": "Peshawar",
            "qta": "Quetta"
        }
        
        query_clean = city_name.strip().lower()
        if query_clean in short_forms:
            city_name = short_forms[query_clean]

        api_key = getattr(settings, "OPENWEATHER_API_KEY", None) or __import__("os").getenv("OPENWEATHER_API_KEY")
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name},PK&units=metric&appid={api_key}"
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                "name": data["name"],
                "temperature_c": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "condition": data["weather"][0]["description"],
                "confidence": "high"
            }
        else:
            return {"error": f"Could not fetch live data for {city_name}"}