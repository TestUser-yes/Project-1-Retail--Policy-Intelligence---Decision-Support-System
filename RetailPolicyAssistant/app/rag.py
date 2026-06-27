from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel


class SourceChunk(BaseModel):
    source: str
    section: str
    text: str


class RAGResult(BaseModel):
    answer: str
    confidence: float
    sources: list[SourceChunk]


NOT_FOUND_MESSAGE = "I couldn't find that information in the company policy."
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHUNKS_FILE = PROJECT_ROOT / "data" / "chunks.json"


def load_policy_chunks() -> list[dict[str, str]]:
    if not CHUNKS_FILE.exists():
        return []

    return json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))


def answer_from_policy_context(question: str) -> RAGResult:
    policy_chunks = load_policy_chunks()
    lower_question = question.lower()

    if not policy_chunks:
        return RAGResult(answer=NOT_FOUND_MESSAGE, confidence=0.0, sources=[])

    tokens = [word.strip(".,?!)('" ) for word in lower_question.split() if len(word) > 3]
    matches: list[dict[str, str]] = []

    for chunk in policy_chunks:
        chunk_text = f"{chunk.get('source', '')} {chunk.get('section', '')} {chunk.get('text', '')}".lower()
        if any(term in chunk_text for term in tokens):
            matches.append(chunk)
            continue
        if any(term in chunk_text for term in ("policy", "retention", "audit", "vendor", "compliance", "review", "legal hold", "restricted")) and any(keyword in lower_question for keyword in ("policy", "retention", "audit", "vendor", "compliance", "review", "legal hold", "restricted")):
            matches.append(chunk)

    if not matches:
        return RAGResult(answer=NOT_FOUND_MESSAGE, confidence=0.0, sources=[])

    answer_lines = []
    sources = []
    for chunk in matches[:3]:
        answer_lines.append(chunk["text"])
        sources.append(
            SourceChunk(
                source=chunk.get("source", "policy document"),
                section=chunk.get("section", "policy section"),
                text=chunk.get("text", ""),
            )
        )

    return RAGResult(
        answer=" ".join(answer_lines),
        confidence=0.8,
        sources=sources,
    )

