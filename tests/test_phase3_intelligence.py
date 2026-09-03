from __future__ import annotations

from datetime import datetime, timezone
import pytest

from app.data.models import TemperatureReading
from app.services.risk_scoring import calculate_risk
from app.services.hotspot_detection import detect_hotspots
from app.ai.agent_tools import AgentTools
from app.ai.agent import HeatGuardAgent


@pytest.fixture
def sample_readings() -> list[TemperatureReading]:
    now = datetime.now(timezone.utc)
    return [
        TemperatureReading(
            location_id="loc-1",
            name="Cool Area",
            latitude=33.7,
            longitude=73.0,
            temperature_c=32.0,
            timestamp=now,
            source="mock",
            confidence="high",
        ),
        TemperatureReading(
            location_id="loc-2",
            name="Hot Area",
            latitude=33.6,
            longitude=73.1,
            temperature_c=43.5,
            timestamp=now,
            source="mock",
            confidence="high",
        ),
    ]


def test_risk_scoring(sample_readings):
    # Test low risk
    risk_low = calculate_risk(sample_readings[0])
    assert risk_low.level == "Low"
    assert 0 <= risk_low.score <= 100

    # Test extreme risk
    risk_extreme = calculate_risk(sample_readings[1])
    assert risk_extreme.level == "Extreme"
    assert risk_extreme.score > 75


def test_hotspot_detection(sample_readings):
    hotspots = detect_hotspots(sample_readings, top_n=1)
    assert len(hotspots) == 1
    assert hotspots[0].name == "Hot Area"
    assert hotspots[0].temperature_c == 43.5
    assert hotspots[0].delta_vs_baseline_c > 0


def test_agent_tools(sample_readings):
    tools = AgentTools()
    risk_res = tools.get_location_risk("Blue Area")
    assert "error" not in risk_res or "location_id" in risk_res

    hotspots = tools.get_top_hotspots(n=2)
    assert isinstance(hotspots, list)
    assert len(hotspots) <= 2


def test_agent_comparison():
    tools = AgentTools()
    comp = tools.compare_locations("Blue Area", "Margalla Hills")
    assert "temperature_delta_c" in comp or "error" in comp


def test_agent_fallback():
    agent = HeatGuardAgent()
    response = agent.answer_query("What is the risk in Blue Area?")
    assert isinstance(response, dict)
    assert "hotspots" in response
    assert "recommendation" in response
    assert "confidence" in response