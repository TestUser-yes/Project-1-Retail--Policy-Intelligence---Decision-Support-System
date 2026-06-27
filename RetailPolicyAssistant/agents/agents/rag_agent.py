"""RAG agent placeholder."""

from dataclasses import dataclass


@dataclass
class RAGAnswer:
    answer: str
    confidence: float
    sources: list[dict[str, str]]


def retrieve_answer(question: str) -> RAGAnswer:
    return RAGAnswer(
        answer="I couldn't find that information in the company policy.",
        confidence=0.0,
        sources=[],
    )
