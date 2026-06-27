"""Escalation agent placeholder."""


def should_escalate(risk_level: str, confidence: float) -> bool:
    return risk_level == "high" or confidence < 0.5
