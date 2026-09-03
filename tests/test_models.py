from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.data.models import AIAnalysis, Hotspot, RiskScore, TemperatureReading


def _valid_reading_kwargs():
    return dict(
        location_id="loc-1",
        name="Test Location",
        latitude=33.7,
        longitude=73.05,
        temperature_c=38.5,
        timestamp=datetime.now(timezone.utc),
        source="mock",
        confidence="high",
    )


def test_valid_temperature_reading_constructs():
    reading = TemperatureReading(**_valid_reading_kwargs())
    assert reading.temperature_c == 38.5
    assert reading.source == "mock"


def test_temperature_out_of_bounds_rejected():
    kwargs = _valid_reading_kwargs()
    kwargs["temperature_c"] = 150.0
    with pytest.raises(ValidationError):
        TemperatureReading(**kwargs)


def test_invalid_latitude_rejected():
    kwargs = _valid_reading_kwargs()
    kwargs["latitude"] = 999.0
    with pytest.raises(ValidationError):
        TemperatureReading(**kwargs)


def test_invalid_source_literal_rejected():
    kwargs = _valid_reading_kwargs()
    kwargs["source"] = "totally_fake_source"
    with pytest.raises(ValidationError):
        TemperatureReading(**kwargs)


def test_risk_score_bounds_enforced():
    with pytest.raises(ValidationError):
        RiskScore(location_id="loc-1", score=150, level="Extreme", confidence="high")

    score = RiskScore(location_id="loc-1", score=87, level="Extreme", confidence="high")
    assert score.score == 87


def test_ai_analysis_requires_valid_priority():
    with pytest.raises(ValidationError):
        AIAnalysis(
            location_id="loc-1",
            temperature=41.0,
            risk_score=87,
            risk_level="Extreme",
            reasoning="Sample reasoning grounded in provided data.",
            priority="Super Critical",  # not in allowed Literal set
            data_confidence="high",
        )


def test_hotspot_constructs_with_required_fields():
    hotspot = Hotspot(
        location_id="loc-1",
        name="Test Location",
        temperature_c=43.2,
        delta_vs_baseline_c=6.4,
        risk_level="Extreme",
        suggested_intervention_type="cooling_center",
    )
    assert hotspot.delta_vs_baseline_c == 6.4
