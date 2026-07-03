"""Orchestrator for demo: routes queries without calling external services."""

import uuid
from app.observability.logger import AgentLogger
from app.observability.metrics import Metrics
from app.repositories.ai_repo import AIRepository
from app.core.cost_tracking import get_cost_tracker
from app.core.slo_tracker import get_slo_tracker


class Orchestrator:
    def __init__(self, db):
        self.db = db
        self.logger = AgentLogger()
        self.metrics = Metrics()
        self.ai_repo = AIRepository(self.db)
        self.cost_tracker = get_cost_tracker()
        self.slo_tracker = get_slo_tracker()

        # Keywords for relevance detection
        self.policy_keywords = [
            "policy", "procedure", "rule", "guideline", "process",
            "protocol", "standard", "requirement", "compliance",
            "approval", "authorization", "permission", "access",
        ]
        self.vendor_keywords = [
            "vendor", "supplier", "partner", "cost", "price",
            "budget", "rate", "fee", "contract", "invoice",
            "payment", "terms", "discount", "wholesale",
        ]
        self.retail_keywords = [
            "refund", "return", "exchange", "customer", "employee",
            "discount", "promotion", "sale", "inventory", "stock",
            "shipping", "delivery", "warehouse", "store", "outlet",
        ]

    def run(self, query: str):
        """Process query and return demo response."""
        query_id = str(uuid.uuid4())[:8]
        try:
            self.metrics.start_timer()
            self.logger.log("input", {"query": query, "query_id": query_id})

            # Check if query is relevant to the system
            is_relevant = self._is_query_relevant(query)
            self.logger.log("relevance_check", {"relevant": is_relevant})

            # Detect intent from keywords
            intent = self._detect_intent(query)
            intent_result = {"intent": intent, "reason": f"Query classified as {intent}"}
            self.logger.log("intent", intent_result)

            # Generate response based on intent
            if intent == "sql":
                result = self._handle_sql_query(query)
                route = "sql"
            elif intent == "rag":
                result = self._handle_rag_query(query)
                route = "rag"
            else:
                result = self._handle_hybrid_query(query)
                route = "hybrid"

            self.logger.log("execution", {"result": result})

            # Risk assessment
            risk_level = "high" if not is_relevant else "low"
            risk_reason = "Query is out-of-scope for this system" if not is_relevant else "Routine query"
            risk_result = {"risk_level": risk_level, "reason": risk_reason}
            self.logger.log("risk", risk_result)

            # Determine escalation
            escalation_needed, escalation_reason = self._check_escalation_needed(
                is_relevant=is_relevant,
                risk_level=risk_level,
            )
            escalation_result = {
                "escalate": escalation_needed,
                "reason": escalation_reason,
            }
            self.logger.log("escalation", escalation_result)

            # Get latency and record SLO metrics
            latency = self.metrics.end_timer()
            slo_metrics = self.slo_tracker.record_latency(latency)

            # Record cost tracking (currently $0 for local Ollama)
            estimated_tokens = len(query.split()) + 50
            self.cost_tracker.record_query(
                query_id=query_id,
                query_text=query,
                embedding_tokens=estimated_tokens,
                completion_tokens=50,
                embedding_cost=0.0,
                completion_cost=0.0,
            )

            # Record SLO events
            self.slo_tracker.record_query_outcome(success=True)
            if escalation_needed:
                self.slo_tracker.record_escalation()

            # Get cost summary for response
            cost_summary = self.cost_tracker.get_summary()
            slo_summary = self.slo_tracker.get_summary()

            # Build response with SLO metrics
            return {
                "query": query,
                "intent": {
                    "intent": intent,
                    "reason": intent_result.get("reason", ""),
                },
                "route": route,
                "result": {
                    "result": str(result),
                },
                "risk": {
                    "risk_level": risk_result.get("risk_level", "low"),
                    "reason": risk_result.get("reason", ""),
                },
                "escalate": escalation_result.get("escalate", False),
                "escalation_reason": escalation_result.get("reason", ""),
                "latency_seconds": latency,
                "cost_usd": 0.0,
                "budget_remaining_usd": cost_summary.budget_remaining,
                "budget_percent_used": cost_summary.budget_usage_percent,
                "slo_metrics": {
                    "latency_ms": slo_metrics.latency_ms,
                    "target_latency_ms": slo_metrics.target_latency_ms,
                    "slo_status": slo_metrics.slo_status,
                },
                "slo_summary": slo_summary,
            }

        except Exception as exc:
            self.logger.log("error", {"error": str(exc)})
            latency = self.metrics.end_timer()
            return {
                "query": query,
                "intent": {"intent": "rag", "reason": "Error fallback"},
                "route": "rag",
                "result": {"result": f"Error: {str(exc)[:100]}"},
                "risk": {"risk_level": "low", "reason": "Error"},
                "escalate": False,
                "escalation_reason": "",
                "latency_seconds": latency,
                "slo_metrics": {
                    "latency_ms": latency * 1000,
                    "target_latency_ms": 2000.0,
                    "slo_status": "fail",
                },
            }

    def _is_query_relevant(self, query: str) -> bool:
        """Check if query is relevant to retail policies/vendors.

        Returns:
            True if query is about policies, vendors, or retail operations
            False if query is out-of-scope
        """
        query_lower = query.lower()
        all_keywords = (
            self.policy_keywords +
            self.vendor_keywords +
            self.retail_keywords
        )
        return any(keyword in query_lower for keyword in all_keywords)

    def _check_escalation_needed(
        self,
        is_relevant: bool,
        risk_level: str,
    ) -> tuple[bool, str]:
        """Determine if query should be escalated.

        Returns:
            (escalate: bool, reason: str)
        """
        if not is_relevant:
            return True, "Query is out-of-scope for this system"
        if risk_level == "high":
            return True, "Query flagged as high-risk, requires compliance review"
        return False, ""

    def _detect_intent(self, query: str) -> str:
        """Detect query intent from keywords."""
        query_lower = query.lower()
        if any(w in query_lower for w in self.vendor_keywords):
            return "sql"
        elif any(w in query_lower for w in self.policy_keywords):
            return "rag"
        return "hybrid"

    def _handle_rag_query(self, query: str) -> str:
        """Handle RAG query."""
        return f"Policy documentation: {query[:40]}... Complies with retail industry standards."

    def _handle_sql_query(self, query: str) -> str:
        """Handle SQL query."""
        return f"Database results: {query[:40]}... Found 12 vendors with costs $3-5K/month."

    def _handle_hybrid_query(self, query: str) -> str:
        """Handle hybrid query."""
        return f"Analysis: {query[:40]}... Policy compliant, cost optimized, vendor approved."
