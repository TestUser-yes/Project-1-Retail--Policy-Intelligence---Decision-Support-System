from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.orchestrator import Orchestrator


router = APIRouter()


# -----------------------------
# Request Schema
# -----------------------------
class AskRequest(BaseModel):
    query: str


class IntentModel(BaseModel):
    intent: str
    reason: str


class RiskModel(BaseModel):
    risk_level: str
    reason: str


class ResultModel(BaseModel):
    result: str


# -----------------------------
# Response Schema
# -----------------------------
class AskResponse(BaseModel):
    query: str
    intent: IntentModel
    route: str
    result: ResultModel
    risk: RiskModel
    escalate: bool
    latency_seconds: float


# -----------------------------
# MAIN ENDPOINT (NEW SYSTEM)
# -----------------------------
@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "system": "Retail Policy AI",
        "agents": "active",
        "db": "connected",
    }


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest, db: Session = Depends(get_db)):
    query = request.query

    orchestrator = Orchestrator(db=db)
    response = orchestrator.run(query)
    return AskResponse(
        query=response["query"],
        intent=response["intent"],
        route=response["route"],
        result=response["result"],
        risk=response["risk"],
        escalate=response["escalate"],
        latency_seconds=response.get("latency_seconds", response.get("latency", 0.0)),
    )
