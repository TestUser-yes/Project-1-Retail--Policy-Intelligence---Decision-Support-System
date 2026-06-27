"""
API entrypoint for Retail Policy Intelligence System.
"""

from fastapi import FastAPI

from app.router import route_query
from app.rag import RAGResult, answer_from_policy_context
from app.sql import answer_from_database

app = FastAPI(
    title="Retail Policy Intelligence & Decision Support System",
    version="1.0.0"
)


def execute_intent(query: str, intent: str) -> RAGResult:
    if intent == "sql":
        return answer_from_database(query)
    if intent == "hybrid":
        sql_result = answer_from_database(query)
        rag_result = answer_from_policy_context(query)
        if sql_result.answer and rag_result.answer:
            combined_answer = f"{sql_result.answer} {rag_result.answer}"
            combined_sources = sql_result.sources + rag_result.sources
            combined_confidence = max(sql_result.confidence, rag_result.confidence)
            return RAGResult(answer=combined_answer, confidence=combined_confidence, sources=combined_sources)
        return sql_result if sql_result.answer else rag_result
    return answer_from_policy_context(query)


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask_question(payload: dict):
    """
    Main entrypoint for policy + compliance questions.
    """

    question = payload.get("question", "")

    routing = route_query(question)
    result = execute_intent(question, routing["intent"])

    return {
        "question": question,
        "route": routing["intent"],
        "risk_level": routing["risk_level"],
        "reason": routing["reason"],
        "answer": result.answer,
        "confidence": result.confidence,
        "escalate": routing["escalate"]
    }
