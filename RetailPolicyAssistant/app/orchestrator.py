"""Orchestrator for demo: routes queries without calling external services."""

from app.observability.logger import AgentLogger
from app.observability.metrics import Metrics
from app.repositories.ai_repo import AIRepository


class Orchestrator:
    def __init__(self, db):
        self.db = db
        self.logger = AgentLogger()
        self.metrics = Metrics()
        self.ai_repo = AIRepository(self.db)

    def run(self, query: str):
        """Process query and return demo response."""
        try:
            self.metrics.start_timer()
            self.logger.log("input", {"query": query})

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

            # Mock risk assessment
            risk_result = {"risk_level": "low", "reason": "Routine query"}
            self.logger.log("risk", risk_result)

            # Mock escalation
            escalation_result = {"escalate": False}

            # Get latency
            latency = self.metrics.end_timer()

            # Build response
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
                "latency_seconds": latency,
            }

        except Exception as exc:
            self.logger.log("error", {"error": str(exc)})
            return {
                "query": query,
                "intent": {"intent": "rag", "reason": "Error fallback"},
                "route": "rag",
                "result": {"result": f"Error: {str(exc)[:100]}"},
                "risk": {"risk_level": "low", "reason": "Error"},
                "escalate": False,
                "latency_seconds": 0,
            }

    def _detect_intent(self, query: str) -> str:
        """Detect query intent from keywords."""
        query_lower = query.lower()
        if any(w in query_lower for w in ["vendor", "supplier", "cost", "price", "budget"]):
            return "sql"
        elif any(w in query_lower for w in ["policy", "process", "procedure", "rule", "guideline"]):
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
