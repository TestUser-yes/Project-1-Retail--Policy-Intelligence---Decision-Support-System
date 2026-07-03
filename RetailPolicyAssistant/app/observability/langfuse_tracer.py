"""
Langfuse integration for distributed tracing and observability.
Traces all LLM calls, queries, and system operations.
"""

import os
import json
import time
from typing import Any, Dict, Optional, List
from datetime import datetime
from functools import wraps

from langfuse import Langfuse


class LangfuseTracer:
    """
    Wrapper around Langfuse for tracing and observability.
    Handles trace initialization, span creation, and metric recording.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LangfuseTracer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")
        self.public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
        self.host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

        # Determine if Langfuse is enabled
        self.enabled = bool(self.secret_key and self.public_key)

        # Initialize Langfuse client only if enabled
        if self.enabled:
            self.client = Langfuse(
                secret_key=self.secret_key,
                public_key=self.public_key,
                host=self.host,
            )
        else:
            self.client = None

        self._initialized = True

    def create_trace(
        self,
        name: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new trace for a request/operation.

        Args:
            name: Trace name (e.g., "ask_query", "rag_pipeline")
            user_id: User making the request
            session_id: Conversation/session ID
            metadata: Additional metadata to attach

        Returns:
            Trace object/ID for use in child spans
        """
        if not self.enabled:
            return {"trace_id": f"local-{int(time.time() * 1000)}"}

        trace_metadata = metadata or {}
        trace_metadata.update({
            "user_id": user_id,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
        })

        trace = self.client.trace(
            name=name,
            user_id=user_id,
            session_id=session_id,
            metadata=trace_metadata,
        )

        return trace

    def create_span(
        self,
        trace: Any,
        name: str,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        span_type: str = "span",
        metadata: Optional[Dict[str, Any]] = None,
        level: str = "INFO",
    ) -> Any:
        """
        Create a span within a trace.

        Args:
            trace: Parent trace object
            name: Span name
            input_data: Input to the operation
            output_data: Output from the operation
            span_type: Type of span (span, llm, generation, evaluation)
            metadata: Additional metadata
            level: Log level

        Returns:
            Span object for nesting
        """
        if not self.enabled or not trace:
            return None

        span_metadata = metadata or {}

        span = trace.span(
            name=name,
            input=input_data,
            metadata=span_metadata,
            level=level,
        )

        if output_data:
            span.end(output=output_data)

        return span

    def log_llm_call(
        self,
        trace: Any,
        model: str,
        prompt: str,
        completion: str,
        tokens_used: Optional[Dict[str, int]] = None,
        cost_usd: float = 0.0,
        latency_ms: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Log an LLM API call.

        Args:
            trace: Parent trace
            model: Model name
            prompt: Input prompt
            completion: Model output
            tokens_used: Token usage dict with keys: prompt_tokens, completion_tokens
            cost_usd: Cost of the call
            latency_ms: Latency in milliseconds
            metadata: Additional metadata

        Returns:
            Generation object
        """
        if not self.enabled or not trace:
            return None

        tokens_used = tokens_used or {}
        meta = metadata or {}
        meta.update({
            "model": model,
            "tokens_used": tokens_used,
            "cost_usd": cost_usd,
            "latency_ms": latency_ms,
        })

        generation = trace.generation(
            name=f"llm-{model}",
            model=model,
            input={"prompt": prompt},
            output={"completion": completion},
            usage={
                "prompt_tokens": tokens_used.get("prompt_tokens", 0),
                "completion_tokens": tokens_used.get("completion_tokens", 0),
                "total_tokens": tokens_used.get("total_tokens", 0),
            },
            cost={
                "input": tokens_used.get("prompt_tokens", 0) * 0.00001,
                "output": tokens_used.get("completion_tokens", 0) * 0.00002,
            },
            metadata=meta,
        )

        return generation

    def log_query_routing(
        self,
        trace: Any,
        query: str,
        intent: str,
        route: str,
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Log query routing decision.

        Args:
            trace: Parent trace
            query: The query
            intent: Detected intent
            route: Selected route (rag, sql, hybrid)
            confidence: Routing confidence
            metadata: Additional metadata

        Returns:
            Span object
        """
        if not self.enabled or not trace:
            return None

        meta = metadata or {}
        meta.update({
            "intent": intent,
            "route": route,
            "confidence": confidence,
        })

        span = trace.span(
            name="query-routing",
            input={"query": query},
            output={
                "intent": intent,
                "route": route,
                "confidence": confidence,
            },
            metadata=meta,
        )

        return span

    def log_rag_retrieval(
        self,
        trace: Any,
        query: str,
        documents_retrieved: List[str],
        scores: Optional[List[float]] = None,
        latency_ms: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Log RAG document retrieval.

        Args:
            trace: Parent trace
            query: Search query
            documents_retrieved: List of retrieved documents
            scores: Relevance scores for each document
            latency_ms: Retrieval latency
            metadata: Additional metadata

        Returns:
            Span object
        """
        if not self.enabled or not trace:
            return None

        scores = scores or [1.0] * len(documents_retrieved)
        meta = metadata or {}
        meta.update({
            "num_documents": len(documents_retrieved),
            "latency_ms": latency_ms,
        })

        span = trace.span(
            name="rag-retrieval",
            input={"query": query},
            output={
                "documents": documents_retrieved[:3],  # Show top 3
                "scores": scores[:3],
                "total_documents": len(documents_retrieved),
            },
            metadata=meta,
        )

        return span

    def log_risk_assessment(
        self,
        trace: Any,
        query: str,
        risk_level: str,
        risk_factors: List[str],
        escalation_required: bool,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Log risk assessment results.

        Args:
            trace: Parent trace
            query: The query
            risk_level: Risk level (low, medium, high, critical)
            risk_factors: List of identified risk factors
            escalation_required: Whether human escalation is needed
            metadata: Additional metadata

        Returns:
            Span object
        """
        if not self.enabled or not trace:
            return None

        meta = metadata or {}
        meta.update({
            "risk_level": risk_level,
            "escalation_required": escalation_required,
            "num_risk_factors": len(risk_factors),
        })

        span = trace.span(
            name="risk-assessment",
            input={"query": query},
            output={
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "escalation_required": escalation_required,
            },
            metadata=meta,
        )

        return span

    def log_guardrail_check(
        self,
        trace: Any,
        query: str,
        is_safe: bool,
        violations: List[str],
        risk_score: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Log guardrail validation results.

        Args:
            trace: Parent trace
            query: The query checked
            is_safe: Whether query passed guardrails
            violations: List of detected violations
            risk_score: Overall risk score (0-1)
            metadata: Additional metadata

        Returns:
            Span object
        """
        if not self.enabled or not trace:
            return None

        meta = metadata or {}
        meta.update({
            "is_safe": is_safe,
            "num_violations": len(violations),
            "risk_score": risk_score,
        })

        span = trace.span(
            name="guardrail-check",
            input={"query": query},
            output={
                "is_safe": is_safe,
                "violations": violations,
                "risk_score": risk_score,
            },
            metadata=meta,
        )

        return span

    def log_rate_limit(
        self,
        trace: Any,
        user_id: str,
        endpoint: str,
        allowed: bool,
        tokens_remaining: int,
        limit: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Log rate limiting decision.

        Args:
            trace: Parent trace
            user_id: User ID
            endpoint: API endpoint
            allowed: Whether request was allowed
            tokens_remaining: Tokens left after this request
            limit: Rate limit
            metadata: Additional metadata

        Returns:
            Span object
        """
        if not self.enabled or not trace:
            return None

        meta = metadata or {}
        meta.update({
            "user_id": user_id,
            "endpoint": endpoint,
            "tokens_remaining": tokens_remaining,
        })

        span = trace.span(
            name="rate-limit-check",
            input={"user_id": user_id, "endpoint": endpoint},
            output={
                "allowed": allowed,
                "tokens_remaining": tokens_remaining,
                "limit": limit,
            },
            metadata=meta,
        )

        return span

    def log_cost(
        self,
        trace: Any,
        cost_usd: float,
        budget_remaining: float,
        budget_used_percent: float,
        tokens: Dict[str, int],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Log cost tracking information.

        Args:
            trace: Parent trace
            cost_usd: Cost of this operation
            budget_remaining: Budget remaining
            budget_used_percent: Percentage of budget used
            tokens: Token breakdown
            metadata: Additional metadata

        Returns:
            Span object
        """
        if not self.enabled or not trace:
            return None

        meta = metadata or {}
        meta.update({
            "cost_usd": cost_usd,
            "budget_remaining": budget_remaining,
            "budget_used_percent": budget_used_percent,
        })

        span = trace.span(
            name="cost-tracking",
            input=tokens,
            output={
                "cost_usd": cost_usd,
                "budget_remaining": budget_remaining,
                "budget_used_percent": budget_used_percent,
            },
            metadata=meta,
        )

        return span

    def flush(self):
        """Flush all pending traces to Langfuse."""
        if self.enabled:
            self.client.flush()


# Global instance
_tracer = None


def get_tracer() -> LangfuseTracer:
    """Get or create global tracer instance."""
    global _tracer
    if _tracer is None:
        _tracer = LangfuseTracer()
    return _tracer


def trace_query(func):
    """Decorator to trace a query processing function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        tracer = get_tracer()
        user_id = kwargs.get("user_id") or (args[0] if args else None)
        session_id = kwargs.get("session_id") or (args[1] if len(args) > 1 else None)

        trace = tracer.create_trace(
            name=func.__name__,
            user_id=str(user_id),
            session_id=str(session_id),
        )

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            tracer.flush()

    return wrapper
