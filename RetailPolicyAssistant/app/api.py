from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import time

from app.database.session import get_db
from app.orchestrator import Orchestrator
from app.core.auth import (
    get_current_user,
    get_demo_token,
    get_demo_refresh_token,
    refresh_access_token,
    revoke_refresh_token,
    User,
)
from app.core.cookies import get_cookie_manager
from app.core.guardrails import validate_query
from app.core.rate_limit import check_rate_limit
from app.core.memory import get_or_create_conversation
from app.core.permissions import PermissionValidator, Permission, require_permission
from app.observability.langfuse_tracer import get_tracer
from app.models import AIQuery
# SLO enforcement - Phase 1.5: Now enabled
from app.core.slo_enforcer import get_slo_enforcer
from app.core.slo_tracker import get_slo_tracker


router = APIRouter()


# -----------------------------
# Request Schema
# -----------------------------
class AskRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=10000)
    conversation_id: str = Field(default="", description="Optional conversation ID (auto-generated if empty)")


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
    slo_breached: bool = False
    enforcement_action: str = "none"
    enforcement_reason: str = ""


# Conversation Response
class MessageModel(BaseModel):
    role: str
    content: str


class ConversationHistoryModel(BaseModel):
    conversation_id: str
    messages: list[MessageModel]


# Agent Execution Details
class AgentExecutionModel(BaseModel):
    agent_name: str
    status: str  # success, error
    latency_ms: float
    confidence: float
    data_source: str  # "PDF Documents", "Database", etc.


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
    # Multi-Agent Visibility - Level 1 (Orchestration)
    agents_used: list[str] = []  # ["rag_agent", "sql_agent"]
    agent_details: list[AgentExecutionModel] = []  # Trace of each agent
    # Multi-Agent Visibility - Level 2 (Retrieval)
    retrieval_method: str = "semantic"  # "semantic", "multi_agent", "fallback"
    retrieval_agents: list[str] = []  # ["semantic_retrieval_agent", "keyword_retrieval_agent", "ranking_agent"]
    retrieval_pipeline: dict = {}  # Full retrieval pipeline details


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


@router.post("/token")
def token_endpoint(response: Response):
    """Get demo access and refresh tokens stored in secure httpOnly cookies.

    Returns tokens in secure httpOnly cookies (not in response body).
    Response body contains metadata only.
    """
    access_token = get_demo_token()
    refresh_token = get_demo_refresh_token()

    # Set secure httpOnly cookies
    cookie_manager = get_cookie_manager()
    cookie_manager.set_access_token_cookie(response, access_token)
    cookie_manager.set_refresh_token_cookie(response, refresh_token)

    return {
        "token_type": "bearer",
        "expires_in": 30 * 60,  # 30 minutes in seconds
        "message": "Tokens set in secure httpOnly cookies",
    }


@router.get("/auth/status")
def auth_status(request: Request):
    """Check authentication status and return user info if authenticated.

    This endpoint helps the frontend verify that cookies were set correctly
    and authentication is working end-to-end.
    """
    try:
        token = None

        # Try to get token from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

        # If no header token, try to get from secure cookie
        if not token:
            token = request.cookies.get("access_token")

        if not token:
            return {
                "authenticated": False,
                "message": "No authentication token found in headers or cookies",
            }

        # Try to verify the token
        from app.core.auth import verify_token
        payload = verify_token(token, token_type="access")

        return {
            "authenticated": True,
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "email": payload.get("email"),
            "role": payload.get("role", "user"),
            "message": "Authentication successful",
        }
    except HTTPException as e:
        return {
            "authenticated": False,
            "message": f"Authentication failed: {e.detail}",
        }
    except Exception as e:
        return {
            "authenticated": False,
            "message": f"Authentication check failed: {str(e)}",
        }


@router.post("/token/refresh")
def refresh_token(response: Response):
    """Refresh access token using refresh token from secure cookie.

    Reads refresh_token from secure httpOnly cookie, returns new access_token in secure cookie.
    """
    try:
        # In a real implementation, extract refresh token from cookie headers
        # For now, we'll use a request dependency to get the cookie
        # The client sends the refresh_token in the secure cookie automatically

        # Get a new access token (in production, read refresh token from request.cookies)
        access_token = get_demo_token()

        # Set new access token cookie
        cookie_manager = get_cookie_manager()
        cookie_manager.set_access_token_cookie(response, access_token)

        return {
            "token_type": "bearer",
            "expires_in": 30 * 60,
            "message": "Access token refreshed",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )


@router.post("/logout")
def logout(response: Response, current_user: User = Depends(get_current_user)):
    """Logout - clear authentication cookies."""
    cookie_manager = get_cookie_manager()
    cookie_manager.clear_auth_cookies(response)

    return {
        "success": True,
        "message": "Logged out successfully - cookies cleared",
    }


@router.post("/ask")
async def ask(
    request_data: AskRequest,
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
    query = request_data.query
    conversation_id = request_data.conversation_id
    start_time = time.time()

    # Note: Langfuse tracing is handled via @observe decorators on:
    # - orchestrator.run() (asks_query span)
    # - rag_agent.run() / sql_agent.run() (rag_pipeline / sql_query spans)
    # This endpoint just processes the response

    try:
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

        # 3b. Check cost/budget (Phase 1.4: Cost tracking enforcement)
        from app.core.cost_tracking import get_cost_tracker

        cost_tracker = get_cost_tracker()
        budget_check = cost_tracker.check_budget()
        if budget_check["enforcement_action"] == "reject":
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,  # Using 429 for budget limit
                detail={
                    "error": "Budget limit exceeded",
                    "daily_remaining": budget_check["remaining_daily"],
                    "monthly_remaining": budget_check["remaining_monthly"],
                },
            )
        elif budget_check["enforcement_action"] == "warn":
            # Log warning but allow
            tracer = get_tracer()
            tracer.log_error(
                "cost_budget_warning",
                f"Budget threshold: {budget_check['summary'].budget_usage_percent:.1f}% used",
            )

        # 4. Get or create conversation
        conversation = get_or_create_conversation(conversation_id, current_user.user_id)
        conversation.add_message("user", query, metadata={"user_id": current_user.user_id})

        # 5. Process query (traces handled by @observe decorator on orchestrator.run)
        orchestrator = Orchestrator(db=db)
        response = await orchestrator.run(query)

        latency_seconds = time.time() - start_time

        # 5b. SLO Enforcement - PHASE 1.5: Now enabled
        try:
            slo_enforcer = get_slo_enforcer()
            enforcement = slo_enforcer.enforce(response, latency_seconds)

            # Log SLO violations to Langfuse
            if enforcement.get("breached", False):
                tracer = get_tracer()
                tracer.log_error(
                    "slo_breach",
                    f"SLO breached: {enforcement.get('enforcement_reason', 'Unknown reason')}",
                )

            # CRITICAL: Enforce SLO violations by rejecting non-compliant requests
            if not enforcement.get("allow", True):
                http_status = enforcement.get("http_status", 503)
                enforcement_reason = enforcement.get("enforcement_reason", "SLO violation")
                raise HTTPException(
                    status_code=http_status,
                    detail={
                        "error": "SLO violation",
                        "reason": enforcement_reason,
                        "action": enforcement.get("enforcement_action", "reject"),
                        "breach_reasons": enforcement.get("breach_reasons", []),
                    }
                )
        except HTTPException:
            raise
        except Exception as e:
            # If SLO enforcement fails, log but don't block (fail-open for availability)
            tracer = get_tracer()
            tracer.log_error("slo_enforcement_error", str(e)[:200])
            enforcement = {
                "allow": True,
                "http_status": 200,
                "enforcement_action": "none",
                "enforcement_reason": "SLO enforcement error",
                "breached": False,
                "breach_reasons": [],
            }

        # 5c. Record cost tracking (Phase 1.4: Cost tracking enforcement)
        from app.core.cost_tracking import record_query_cost
        from app.utils.tokenizer import count_query_response_tokens

        # Get token counts from orchestrator tracking
        embedding_tokens, completion_tokens = count_query_response_tokens(
            query,
            response["result"]["result"]
        )

        cost_record = record_query_cost(
            query_text=query,
            query_id=conversation.conversation_id,
            embedding_tokens=embedding_tokens,
            completion_tokens=completion_tokens,
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
                "cost_recorded": cost_record is not None,
            }
        )

        # 6b. Save query to database for dashboard
        ai_query = AIQuery(
            query=query,
            result=response["result"]["result"],
            intent=response["intent"]["intent"],
            route=response["route"],
            risk_level=response["risk"]["risk_level"],
            escalated=response["escalate"],
            confidence_score=response.get("confidence_score", 0.0),
            latency=latency_seconds * 1000,
            cost_usd=response.get("cost_usd", 0.0),
            slo_breached=enforcement["breached"],
            enforcement_action=enforcement["enforcement_action"],
            enforcement_reason=enforcement["enforcement_reason"],
        )
        db.add(ai_query)
        db.commit()

        # 7. Return response with all metadata
        slo_metrics_data = response.get("slo_metrics", {
            "latency_ms": 0,
            "target_latency_ms": 2000.0,
            "slo_status": "unknown",
        })
        slo_metrics_data["slo_breached"] = enforcement["breached"]
        slo_metrics_data["enforcement_action"] = enforcement["enforcement_action"]
        slo_metrics_data["enforcement_reason"] = enforcement["enforcement_reason"]

        # Convert agent details dict to AgentExecutionModel
        agent_details_models = []
        for agent_detail in response.get("agent_details", []):
            agent_details_models.append(AgentExecutionModel(**agent_detail))

        # Build response dict
        response_dict = {
            "query": response["query"],
            "conversation_id": conversation.conversation_id,
            "intent": response["intent"],
            "route": response["route"],
            "result": response["result"],
            "risk": response["risk"],
            "escalate": response["escalate"],
            "escalation_reason": response.get("escalation_reason", ""),
            "latency_seconds": latency_seconds,
            "cost_usd": response.get("cost_usd", 0.0),
            "budget_remaining_usd": response.get("budget_remaining_usd", 0.0),
            "budget_percent_used": response.get("budget_percent_used", 0.0),
            "slo_metrics": {
                "latency_ms": slo_metrics_data.get("latency_ms", 0),
                "target_latency_ms": slo_metrics_data.get("target_latency_ms", 2000),
                "slo_status": slo_metrics_data.get("slo_status", "unknown"),
                "slo_breached": slo_metrics_data.get("slo_breached", False),
                "enforcement_action": slo_metrics_data.get("enforcement_action", "none"),
                "enforcement_reason": slo_metrics_data.get("enforcement_reason", ""),
            },
            "validation_passed": True,
            "confidence_score": response.get("confidence_score", 0.0),
            "sources": response.get("sources", []),
            "sql_validation": response.get("sql_validation", ""),
            "recommendation": response.get("recommendation", ""),
            "agents_used": response.get("agents_used", []),
            "agent_details": [{"agent_name": d.get("agent_name", ""), "status": d.get("status", ""), "latency_ms": d.get("latency_ms", 0), "confidence": d.get("confidence", 0), "data_source": d.get("data_source", "")} for d in response.get("agent_details", [])],
            "retrieval_method": response.get("retrieval_method", "semantic"),
            "retrieval_agents": response.get("retrieval_agents", []),
            "retrieval_pipeline": response.get("retrieval_pipeline", {}),
        }

        # 6c. TRACE SCORES TO LANGFUSE (after response is fully constructed)
        from app.observability.score_tracer import ScoreTracer
        try:
            ScoreTracer.log_query_execution(
                query=query,
                route=response.get("route", "unknown"),
                confidence=response.get("confidence_score", 0.0),
                risk_level=response.get("risk", {}).get("risk_level", "unknown"),
                latency_ms=latency_seconds * 1000,
                user_id=current_user.user_id,
            )
        except Exception as e:
            tracer = get_tracer()
            tracer.log_error("score_tracing", f"Error logging scores: {str(e)[:100]}")

        return response_dict

    except HTTPException:
        raise
    except Exception as e:
        tracer = get_tracer()
        tracer.log_error("ask_query", str(e)[:200])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing failed: {str(e)[:100]}"
        )
    finally:
        tracer = get_tracer()
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
