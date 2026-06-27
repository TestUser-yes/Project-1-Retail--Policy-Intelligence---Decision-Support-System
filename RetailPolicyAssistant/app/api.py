from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.router import route_query
from app.rag import RAGResult, answer_from_policy_context
from app.sql import answer_from_database
from app.utils import load_environment


load_environment()

app = FastAPI(
    title="Retail Policy Assistant",
    description="Policy intelligence and decision support API.",
    version="0.1.0",
)


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=3)


class QuestionResponse(BaseModel):
    answer: str
    route: str
    risk_level: str
    confidence: float
    escalate: bool


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
def home() -> dict[str, str]:
    return {"message": "Retail Policy Assistant Running"}


@app.post("/ask", response_model=QuestionResponse)
def ask(request: QuestionRequest) -> QuestionResponse:
    routing = route_query(request.question)
    result = execute_intent(request.question, routing["intent"])

    return QuestionResponse(
        answer=result.answer,
        route=routing["intent"],
        risk_level=routing["risk_level"],
        confidence=result.confidence,
        escalate=routing["escalate"],
    )

