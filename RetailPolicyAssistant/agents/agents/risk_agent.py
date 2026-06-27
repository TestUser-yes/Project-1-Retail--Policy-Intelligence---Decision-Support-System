"""Risk classification agent."""

from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


HIGH_RISK_TERMS = {
    "legal hold",
    "cross-border",
    "restricted jurisdiction",
    "bribery",
    "gift",
    "hospitality",
}


def classify_risk(question: str) -> RiskLevel:
    text = question.lower()
    if any(term in text for term in HIGH_RISK_TERMS):
        return RiskLevel.HIGH
    return RiskLevel.LOW
