from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import uuid

from app.database.session import get_db
from app.orchestrator import Orchestrator
from app.core.auth import get_current_user, get_demo_token, User
from app.core.guardrails import validate_query
from app.core.rate_limit import check_rate_limit
from app.core.memory import get_or_create_conversation
from app.core.permissions import PermissionValidator, Permission, require_permission


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
    latency_seconds: float
    cost_usd: float = 0.0
    budget_remaining_usd: float = 0.0
    budget_percent_used: float = 0.0
    validation_passed: bool = True


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
    """
    query = request.query
    conversation_id = request.conversation_id

    # 1. Check permission
    PermissionValidator.assert_permission(current_user, Permission.ASK_POLICY_QUESTION)

    # 2. Validate input
    is_valid, error_msg = validate_query(query)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Query validation failed: {error_msg}"
        )

    # 3. Check rate limits
    allowed, rate_info = check_rate_limit(current_user.user_id, "/ask")
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Limit: {rate_info['ask_limit']['limit']}/hour"
        )

    # 4. Get or create conversation
    conversation = get_or_create_conversation(conversation_id, current_user.user_id)
    conversation.add_message("user", query, metadata={"user_id": current_user.user_id})

    try:
        # 5. Process query
        orchestrator = Orchestrator(db=db)
        response = orchestrator.run(query)

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
            }
        )

        # 7. Return response with all metadata
        return AskResponse(
            query=response["query"],
            conversation_id=conversation_id,
            intent=response["intent"],
            route=response["route"],
            result=response["result"],
            risk=response["risk"],
            escalate=response["escalate"],
            latency_seconds=response.get("latency_seconds", response.get("latency", 0.0)),
            cost_usd=response.get("cost_usd", 0.0),
            budget_remaining_usd=response.get("budget_remaining_usd", 0.0),
            budget_percent_used=response.get("budget_percent_used", 0.0),
            validation_passed=True,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing failed: {str(e)[:100]}"
        )


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
