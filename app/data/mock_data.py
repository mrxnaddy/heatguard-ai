"""
Mock data for HeatGuard AI.

This data is clearly and permanently labeled source="mock" wherever it
flows through the app — in the data model, and in the UI badge. It is
NEVER presented to the user as live FortyGuard data.

Values are illustrative sample data for demo purposes (loosely modeled
on plausible September conditions and urban heat-island effects for the
Islamabad/Rawalpindi demo pair), not verified real-world measurements.
"""
from __future__ import annotations

from datetime import datetime, timezone

from app.data.models import TemperatureReading

# A fixed "now" would make demos non-reproducible across time zones/days,
# so we mock a stable set of location + temperature pairs and stamp them
# with the current time at read-time (see mock_data.get_mock_readings()).
_MOCK_LOCATIONS: list[dict] = [
    {
        "location_id": "isb-blue-area",
        "name": "Blue Area, Islamabad",
        "latitude": 33.7089,
        "longitude": 73.0563,
        "temperature_c": 41.5,
        "confidence": "high",
    },
    {
        "location_id": "isb-f6-markaz",
        "name": "F-6 Markaz, Islamabad",
        "latitude": 33.7167,
        "longitude": 73.0847,
        "temperature_c": 36.8,
        "confidence": "high",
    },
    {
        "location_id": "isb-margalla-hills",
        "name": "Margalla Hills, Islamabad",
        "latitude": 33.7460,
        "longitude": 73.0551,
        "temperature_c": 32.1,
        "confidence": "high",
    },
    {
        "location_id": "isb-i9-industrial",
        "name": "I-9 Industrial Area, Islamabad",
        "latitude": 33.6650,
        "longitude": 73.0450,
        "temperature_c": 43.2,
        "confidence": "partial",
    },
    {
        "location_id": "rwp-committee-chowk",
        "name": "Committee Chowk, Rawalpindi",
        "latitude": 33.6007,
        "longitude": 73.0679,
        "temperature_c": 42.7,
        "confidence": "high",
    },
    {
        "location_id": "rwp-saddar",
        "name": "Saddar, Rawalpindi",
        "latitude": 33.5983,
        "longitude": 73.0472,
        "temperature_c": 40.9,
        "confidence": "high",
    },
    {
        "location_id": "rwp-bahria-town",
        "name": "Bahria Town, Rawalpindi",
        "latitude": 33.5350,
        "longitude": 73.1200,
        "temperature_c": 37.4,
        "confidence": "partial",
    },
]


def get_mock_readings() -> list[TemperatureReading]:
    """Return the full mock dataset as validated TemperatureReading models."""
    now = datetime.now(timezone.utc)
    return [
        TemperatureReading(
            location_id=loc["location_id"],
            name=loc["name"],
            latitude=loc["latitude"],
            longitude=loc["longitude"],
            temperature_c=loc["temperature_c"],
            timestamp=now,
            source="mock",
            confidence=loc["confidence"],
        )
        for loc in _MOCK_LOCATIONS
    ]


def get_mock_reading(location_id: str) -> TemperatureReading | None:
    """Return a single mock reading by location_id, or None if not found."""
    for reading in get_mock_readings():
        if reading.location_id == location_id:
            return reading
    return None
