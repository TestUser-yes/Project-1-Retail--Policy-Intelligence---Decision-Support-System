"""SQL retrieval agent placeholder."""

from dataclasses import dataclass


@dataclass
class SQLAnswer:
    answer: str
    confidence: float
    sources: list[dict[str, str]]


def query_sql(question: str) -> SQLAnswer:
    return SQLAnswer(
        answer="SQL lookup is not yet implemented.",
        confidence=0.0,
        sources=[],
    )
