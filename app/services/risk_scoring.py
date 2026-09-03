from __future__ import annotations

from app.data.models import Confidence, RiskLevel, RiskScore, TemperatureReading


def calculate_risk(reading: TemperatureReading) -> RiskScore:
    """
    Calculate a deterministic, explainable Heat Risk Score (0-100) 
    and RiskLevel based on hyperlocal temperature and confidence.
    
    Product-defined decision-support metric (not a medical/clinical index).
    Formula:
      - Base score derived linearly from temperature bounds (30°C to 45°C mapped to 0 to 100).
      - Clamped between 0 and 100.
    """
    temp = reading.temperature_c
    
    # Linear mapping from [30.0, 45.0] to [0.0, 100.0]
    raw_score = int((temp - 30.0) / (45.0 - 30.0) * 100.0)
    score = max(0, min(100, raw_score))

    # Determine Risk Level & Thresholds
    if temp < 35.0:
        level: RiskLevel = "Low"
    elif temp < 39.0:
        level: RiskLevel = "Moderate"
    elif temp < 42.0:
        level: RiskLevel = "High"
    else:
        level: RiskLevel = "Extreme"

    return RiskScore(
        location_id=reading.location_id,
        score=score,
        level=level,
        inputs={
            "temperature_c": temp,
            "confidence_weight": reading.confidence,
        },
        confidence=reading.confidence,
    )