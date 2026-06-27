from __future__ import annotations

from typing import Iterable

from app.database import get_db_connection
from app.rag import RAGResult, SourceChunk, NOT_FOUND_MESSAGE


def answer_from_database(question: str) -> RAGResult:
    lower_question = question.lower()

    if "retention" in lower_question or "legal hold" in lower_question:
        return answer_from_retention_records(lower_question)
    if "audit" in lower_question or "log" in lower_question:
        return answer_from_audit_logs(lower_question)
    if "compliance" in lower_question or "review" in lower_question:
        return answer_from_compliance_reviews(lower_question)
    if "vendor" in lower_question or "supplier" in lower_question or "status" in lower_question:
        return answer_from_vendors(lower_question)

    return RAGResult(answer=NOT_FOUND_MESSAGE, confidence=0.0, sources=[])


def answer_from_vendors(lower_question: str) -> RAGResult:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT vendor_id, name, risk_level, status, country FROM vendors")
        rows = cursor.fetchall()

    if not rows:
        return RAGResult(answer=NOT_FOUND_MESSAGE, confidence=0.0, sources=[])

    matching = [row for row in rows if row["name"].lower() in lower_question]
    selected_rows = matching or rows

    lines = []
    for row in selected_rows:
        lines.append(
            f"Vendor {row['name']} is {row['status']} with risk level {row['risk_level']} in {row['country']}."
        )

    return RAGResult(
        answer=" ".join(lines),
        confidence=0.85,
        sources=[
            SourceChunk(
                source="vendors",
                section="vendor lookup",
                text="; ".join(line for line in lines[:2]),
            )
        ],
    )


def answer_from_audit_logs(lower_question: str) -> RAGResult:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT log_id, vendor_id, event, timestamp FROM audit_logs ORDER BY timestamp DESC")
        rows = cursor.fetchall()

    if not rows:
        return RAGResult(answer=NOT_FOUND_MESSAGE, confidence=0.0, sources=[])

    lines = [f"Audit {row['log_id']} for vendor {row['vendor_id']}: {row['event']} at {row['timestamp']}." for row in rows[:3]]

    return RAGResult(
        answer=" ".join(lines),
        confidence=0.8,
        sources=[
            SourceChunk(
                source="audit_logs",
                section="audit lookup",
                text="; ".join(lines[:2]),
            )
        ],
    )


def answer_from_retention_records(lower_question: str) -> RAGResult:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT record_id, data_type, retention_period, legal_hold FROM retention_records")
        rows = cursor.fetchall()

    if not rows:
        return RAGResult(answer=NOT_FOUND_MESSAGE, confidence=0.0, sources=[])

    held_rows = [row for row in rows if row["legal_hold"]]
    if "legal hold" in lower_question and held_rows:
        row = held_rows[0]
        line = (
            f"{row['data_type'].capitalize()} is on legal hold and retained for {row['retention_period']}."
        )
        lines = [line]
    else:
        lines = [
            f"{row['data_type'].capitalize()} is retained for {row['retention_period']} and is {'on legal hold' if row['legal_hold'] else 'not on legal hold'}."
            for row in rows
        ]

    return RAGResult(
        answer=" ".join(lines),
        confidence=0.85,
        sources=[
            SourceChunk(
                source="retention_records",
                section="retention lookup",
                text="; ".join(lines[:2]),
            )
        ],
    )


def answer_from_compliance_reviews(lower_question: str) -> RAGResult:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT review_id, vendor_id, status, findings FROM compliance_reviews")
        rows = cursor.fetchall()

    if not rows:
        return RAGResult(answer=NOT_FOUND_MESSAGE, confidence=0.0, sources=[])

    lines = [
        f"Review {row['review_id']} for vendor {row['vendor_id']} is {row['status']}: {row['findings']}."
        for row in rows
    ]

    return RAGResult(
        answer=" ".join(lines),
        confidence=0.82,
        sources=[
            SourceChunk(
                source="compliance_reviews",
                section="compliance lookup",
                text="; ".join(line for line in lines[:2]),
            )
        ],
    )
