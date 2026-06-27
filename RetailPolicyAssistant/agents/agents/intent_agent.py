"""Intent classification agent."""

from enum import Enum


class Intent(str, Enum):
    POLICY = "policy"
    SQL = "sql"
    HYBRID = "hybrid"


def classify_intent(question: str) -> Intent:
    text = question.lower()
    if "policy" in text or "clause" in text:
        return Intent.POLICY
    if "vendor" in text or "audit" in text:
        return Intent.SQL
    return Intent.HYBRID
