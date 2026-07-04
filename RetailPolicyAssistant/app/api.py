from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import uuid
import time

from app.database.session import get_db
from app.orchestrator import Orchestrator
from app.core.auth import get_current_user, get_demo_token, User
from app.core.guardrails import validate_query
from app.core.rate_limit import check_rate_limit
from app.core.memory import get_or_create_conversation
from app.core.permissions import PermissionValidator, Permission, require_permission
from app.observability.langfuse_tracer import get_tracer
from app.models import AIQuery


router = APIRouter()


# -----------------------------
# Request Schema
# -----------------------------
class AskRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=10000)
    conversation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class IntentModel(BaseModel):
    intent: str
    reason: str


class RiskModel(BaseModel):
    risk_level: str
    reason: str


class ResultModel(BaseModel):
    result: str


class SLOMetricsModel(BaseModel):
    latency_ms: float
    target_latency_ms: float
    slo_status: str  # pass, warning, fail


# Conversation Response
class MessageModel(BaseModel):
    role: str
    content: str


class ConversationHistoryModel(BaseModel):
    conversation_id: str
    messages: list[MessageModel]


# Response Schema
class AskResponse(BaseModel):
    query: str
    conversation_id: str
    intent: IntentModel
    route: str
    result: ResultModel
    risk: RiskModel
    escalate: bool
    escalation_reason: str = ""
    latency_seconds: float
    cost_usd: float = 0.0
    budget_remaining_usd: float = 0.0
    budget_percent_used: float = 0.0
    slo_metrics: SLOMetricsModel
    validation_passed: bool = True
    # Phase 7 fields
    confidence_score: float = 0.0
    sources: list = []
    sql_validation: str = ""
    recommendation: str = ""


# -----------------------------
# MAIN ENDPOINT (NEW SYSTEM)
# -----------------------------
@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "system": "Retail Policy AI",
        "agents": "active",
        "db": "connected",
        "timestamp": "2026-07-03"
    }


@router.get("/token")
def get_token():
    """Get demo token for testing."""
    return {"access_token": get_demo_token(), "token_type": "bearer"}


@router.post("/ask", response_model=AskResponse)
def ask(
    request: AskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ask a policy question (requires authentication).

    Features:
    - Input validation and guardrails
    - Rate limiting per user
    - Cost tracking
    - Conversation memory
    - Permission checking
    - Langfuse observability tracing
    """
    query = request.query
    conversation_id = request.conversation_id
    start_time = time.time()

    # Initialize Langfuse tracer
    tracer = get_tracer()
    trace = tracer.create_trace(
        name="ask-query",
        user_id=current_user.user_id,
        session_id=conversation_id,
        metadata={
            "query_length": len(query),
            "user_role": current_user.role,
        }
    )

    try:
        # 1. Check permission
        PermissionValidator.assert_permission(current_user, Permission.ASK_POLICY_QUESTION)
        tracer.create_span(
            trace,
            "permission-check",
            input_data={"user_id": current_user.user_id, "role": current_user.role},
            output_data={"allowed": True},
        )

        # 2. Validate input
        is_valid, error_msg = validate_query(query)
        if not is_valid:
            tracer.create_span(
                trace,
                "input-validation",
                input_data={"query": query},
                output_data={"is_valid": False, "error": error_msg},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Query validation failed: {error_msg}"
            )

        tracer.create_span(
            trace,
            "input-validation",
            input_data={"query": query},
            output_data={"is_valid": True},
        )

        # 3. Check rate limits
        allowed, rate_info = check_rate_limit(current_user.user_id, "/ask")
        if not allowed:
            tracer.create_span(
                trace,
                "rate-limit-check",
                input_data={"user_id": current_user.user_id, "endpoint": "/ask"},
                output_data={
                    "allowed": False,
                    "limit": rate_info.get('ask_limit', {}).get('limit', 50),
                },
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Limit: {rate_info['ask_limit']['limit']}/hour"
            )

        tracer.create_span(
            trace,
            "rate-limit-check",
            input_data={"user_id": current_user.user_id, "endpoint": "/ask"},
            output_data={
                "allowed": True,
                "tokens_remaining": rate_info.get('ask_limit', {}).get('tokens_remaining', 0),
            },
        )

        # 4. Get or create conversation
        conversation = get_or_create_conversation(conversation_id, current_user.user_id)
        conversation.add_message("user", query, metadata={"user_id": current_user.user_id})

        # 5. Process query
        orchestrator = Orchestrator(db=db)
        response = orchestrator.run(query)

        latency_seconds = time.time() - start_time

        # Log orchestrator response details
        tracer.create_span(
            trace,
            "query-orchestration",
            input_data={"query": query},
            output_data={
                "intent": response["intent"]["intent"],
                "route": response["route"],
                "risk_level": response["risk"]["risk_level"],
                "escalate": response["escalate"],
            },
        )

        # Log cost information
        tracer.log_cost(
            trace,
            cost_usd=response.get("cost_usd", 0.0),
            budget_remaining=response.get("budget_remaining_usd", 0.0),
            budget_used_percent=response.get("budget_percent_used", 0.0),
            tokens={
                "query_length": len(query),
                "response_length": len(response["result"]["result"]),
            },
        )

        # 6. Add response to conversation memory
        conversation.add_message(
            "assistant",
            response["result"]["result"],
            metadata={
                "intent": response["intent"]["intent"],
                "route": response["route"],
                "risk_level": response["risk"]["risk_level"],
                "escalate": response["escalate"],
                "cost_usd": response.get("cost_usd", 0.0),
                "latency_seconds": latency_seconds,
            }
        )

        # 6b. Save query to database for dashboard
        ai_query = AIQuery(
            query=query,
            intent=response["intent"]["intent"],
            route=response["route"],
            risk_level=response["risk"]["risk_level"],
            latency=latency_seconds * 1000,
        )
        db.add(ai_query)
        db.commit()

        # 7. Return response with all metadata
        slo_metrics_data = response.get("slo_metrics", {
            "latency_ms": 0,
            "target_latency_ms": 2000.0,
            "slo_status": "unknown",
        })

        return AskResponse(
            query=response["query"],
            conversation_id=conversation_id,
            intent=response["intent"],
            route=response["route"],
            result=response["result"],
            risk=response["risk"],
            escalate=response["escalate"],
            escalation_reason=response.get("escalation_reason", ""),
            latency_seconds=latency_seconds,
            cost_usd=response.get("cost_usd", 0.0),
            budget_remaining_usd=response.get("budget_remaining_usd", 0.0),
            budget_percent_used=response.get("budget_percent_used", 0.0),
            slo_metrics=SLOMetricsModel(**slo_metrics_data),
            validation_passed=True,
            confidence_score=response.get("confidence_score", 0.0),
            sources=response.get("sources", []),
            sql_validation=response.get("sql_validation", ""),
            recommendation=response.get("recommendation", ""),
        )

    except HTTPException:
        raise
    except Exception as e:
        tracer.create_span(
            trace,
            "error",
            output_data={"error": str(e)[:200]},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing failed: {str(e)[:100]}"
        )
    finally:
        tracer.flush()


@router.get("/conversations/{conversation_id}/history", response_model=ConversationHistoryModel)
def get_conversation_history(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get conversation history (owner or admin only).

    Args:
        conversation_id: Conversation ID

    Returns:
        Conversation with message history
    """
    from app.core.memory import get_conversation

    # Check permission
    PermissionValidator.assert_permission(current_user, Permission.VIEW_QUERY_HISTORY)

    # Get conversation
    conversation = get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Check access (owner or admin)
    if conversation.user_id != current_user.user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    messages = [
        MessageModel(role=m.role, content=m.content)
        for m in conversation.messages
    ]

    return ConversationHistoryModel(
        conversation_id=conversation_id,
        messages=messages
    )
