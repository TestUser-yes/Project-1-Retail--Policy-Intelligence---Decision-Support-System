from __future__ import annotations

from enum import Enum
from pydantic import BaseModel


class Route(str, Enum):
    RAG = "rag"
    SQL = "sql"
    HYBRID = "hybrid"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Classification(BaseModel):
    route: Route
    risk_level: RiskLevel
    reason: str


HIGH_RISK_TERMS = {
    "cross-border",
    "restricted jurisdiction",
    "legal hold",
    "critical-risk",
    "bribery",
    "gift",
    "hospitality",
    "overseas supplier",
    "audit finding",
    "unresolved",
    "legal validation",
}

SQL_TERMS = {
    "vendor",
    "approval status",
    "audit log",
    "retention record",
    "compliance review",
    "record id",
}


def classify_query(question: str) -> Classification:
    text = question.lower()
    is_high_risk = any(term in text for term in HIGH_RISK_TERMS)
    needs_sql = any(term in text for term in SQL_TERMS)
    needs_policy = any(term in text for term in ("policy", "clause", "section", "explain", "allowed"))

    if needs_sql and needs_policy:
        route = Route.HYBRID
    elif needs_sql:
        route = Route.SQL
    else:
        route = Route.RAG

    return Classification(
        route=route,
        risk_level=RiskLevel.HIGH if is_high_risk else RiskLevel.LOW,
        reason="Keyword-based starter classifier; replace with LLM or trained classifier as the project matures.",
    )

