from __future__ import annotations

from types import SimpleNamespace
from app.data.models import Hotspot, RiskScore, TemperatureReading
from app.services.fortyguard_client import FortyGuardClient
from app.services.hotspot_detection import detect_hotspots
from app.services.risk_scoring import calculate_risk


class AgentTools:
    """Encapsulates all deterministic tools available to the AI agent."""

    def __init__(self, client: FortyGuardClient | None = None) -> None:
        self.client = client or FortyGuardClient()

    def get_location_risk(self, location_query: str) -> dict:
        """Get risk score and temperature for a specific location by ID or name."""
        try:
            locations = self.client.get_all_locations()
        except Exception:
            return {"error": "Unable to retrieve location data."}

        match = next(
            (loc for loc in locations if location_query.lower() in loc.name.lower() or location_query.lower() == loc.location_id),
            None,
        )
        if not match:
            return {"error": f"I cannot confirm this from the available data for '{location_query}'."}

        risk = calculate_risk(match)
        return {
            "location_id": match.location_id,
            "name": match.name,
            "temperature_c": match.temperature_c,
            "risk_score": risk.score,
            "risk_level": risk.level,
            "confidence": risk.confidence,
            "source": match.source,
            "timestamp": match.timestamp.isoformat(),
        }

    def get_city_live_risk(self, city_name: str) -> dict:
        """Fetch live weather for any city in Pakistan and calculate risk score."""
        live_data = self.client.get_live_weather(city_name)
        
        if "error" in live_data:
            return live_data

        reading = SimpleNamespace(
            location_id=city_name.lower().replace(" ", "-"),
            name=live_data["name"],
            temperature_c=live_data["temperature_c"],
            confidence=live_data["confidence"]
        )
        
        risk = calculate_risk(reading)
        
        return {
            "name": live_data["name"],
            "temperature_c": live_data["temperature_c"],
            "humidity": live_data["humidity"],
            "condition": live_data["condition"],
            "risk_level": risk.level,
            "risk_score": risk.score,
            "confidence": live_data["confidence"]
        }

    def get_top_hotspots(self, n: int = 3) -> list[dict]:
        """Return top N heat hotspots ranked by relative temperature delta."""
        try:
            locations = self.client.get_all_locations()
        except Exception:
            return []

        hotspots = detect_hotspots(locations, top_n=n)
        return [h.model_dump() for h in hotspots]

    def compare_locations(self, location_a: str, location_b: str) -> dict:
        """Compare temperature and risk between two locations."""
        res_a = self.get_location_risk(location_a)
        res_b = self.get_location_risk(location_b)

        if "error" in res_a or "error" in res_b:
            return {"error": "I cannot confirm this from the available data for one or both locations."}

        return {
            "location_a": res_a,
            "location_b": res_b,
            "temperature_delta_c": round(abs(res_a["temperature_c"] - res_b["temperature_c"]), 2),
            "higher_risk": res_a["name"] if res_a["risk_score"] > res_b["risk_score"] else res_b["name"],
        }