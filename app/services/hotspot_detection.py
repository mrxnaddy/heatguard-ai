from __future__ import annotations

from app.data.models import Hotspot, TemperatureReading
from app.services.risk_scoring import calculate_risk


def detect_hotspots(readings: list[TemperatureReading], top_n: int = 3) -> list[Hotspot]:
    """
    Calculate dataset baseline, temperature deltas, and rank top hotspots.
    Distinguishes relative temperature outliers from absolute danger thresholds.
    """
    if not readings:
        return []

    # Calculate dataset mean baseline
    baseline_temp = sum(r.temperature_c for r in readings) / len(readings)

    # Sort readings by temperature descending (highest relative temperature first)
    sorted_readings = sorted(readings, key=lambda r: r.temperature_c, reverse=True)

    hotspots: list[Hotspot] = []
    for reading in sorted_readings[:top_n]:
        delta = round(reading.temperature_c - baseline_temp, 2)
        risk_score_obj = calculate_risk(reading)

        # Suggest intervention type based on risk level
        if risk_score_obj.level in ("High", "Extreme"):
            intervention = "Immediate cooling station deployment & public advisory"
        elif risk_score_obj.level == "Moderate":
            intervention = "Shade structure enhancement & hydration point check"
        else:
            intervention = "Standard urban heat monitoring"

        hotspots.append(
            Hotspot(
                location_id=reading.location_id,
                name=reading.name,
                temperature_c=reading.temperature_c,
                delta_vs_baseline_c=delta,
                risk_level=risk_score_obj.level,
                suggested_intervention_type=intervention,
            )
        )

    return hotspots