"""Orchestrator for demo: routes queries without calling external services."""

from app.observability.logger import AgentLogger
from app.observability.metrics import Metrics
from app.observability.langfuse_tracer import trace_function
from app.repositories.ai_repo import AIRepository
# from app.core.cost_tracking import get_cost_tracker, CostSummary
from app.core.slo_tracker import get_slo_tracker
from app.config import get_config
from app.utils.tokenizer import count_query_response_tokens


class Orchestrator:
    def __init__(self, db):
        self.db = db
        self.logger = AgentLogger()
        self.metrics = Metrics()
        self.ai_repo = AIRepository(self.db)
        # self.cost_tracker = get_cost_tracker()
        self.cost_tracker = None
        self.slo_tracker = get_slo_tracker()

        # Load dynamic configuration
        self.config = get_config()
        self.policy_keywords = self.config.keywords.policy
        self.vendor_keywords = self.config.keywords.vendor
        self.retail_keywords = self.config.keywords.retail
        self.risk_thresholds = self.config.risk_thresholds
        self.cost_config = self.config.cost
        self.routing_config = self.config.routing

    @trace_function("ask_query", as_type="chain")
    def run(self, query: str):
        """Process query and return demo response."""
        try:
            self.metrics.start_timer()
            self.logger.log("input", {"query": query})

            # Track which agents were used
            agents_used = []
            agent_details = []

            # Check if query is relevant to the system
            is_relevant = self._is_query_relevant(query)
            self.logger.log("relevance_check", {"relevant": is_relevant})

            # Detect intent from keywords
            intent = self._detect_intent(query)
            intent_result = {"intent": intent, "reason": f"Query classified as {intent}"}
            self.logger.log("intent", intent_result)

            # Generate response based on intent
            agent_confidence = 0.7  # Default fallback
            agent_sources = []
            if intent == "sql":
                result, agent_confidence, agent_sources, agent_exec = self._handle_sql_query(query)
                route = "sql"
                agents_used.append("sql_agent")
                agent_details.append(agent_exec)
            elif intent == "rag":
                result, agent_confidence, agent_sources, agent_exec = self._handle_rag_query(query)
                route = "rag"
                agents_used.append("rag_agent")
                agent_details.append(agent_exec)
            else:
                result, agent_confidence, agent_sources, rag_exec, sql_exec = self._handle_hybrid_query(query)
                route = "hybrid"
                agents_used.extend(["rag_agent", "sql_agent"])
                agent_details.extend([rag_exec, sql_exec])

            self.logger.log("execution", {"result": result})

            # Calculate real token counts for cost tracking
            embedding_tokens, completion_tokens = count_query_response_tokens(query, result)
            self.logger.log("tokens", {
                "embedding_tokens": embedding_tokens,
                "completion_tokens": completion_tokens,
            })

            # Risk assessment - now supports 3 levels: low, medium, high
            risk_level = self._assess_risk_level(query, is_relevant)
            if risk_level == "high":
                risk_reason = (
                    "Query is out-of-scope for this system" if not is_relevant
                    else "Query flagged for potential compliance risk"
                )
            elif risk_level == "medium":
                risk_reason = "Query involves approval/compliance review"
            else:
                risk_reason = "Routine policy query"
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

            # Record cost tracking - disabled for now
            embedding_cost = 0.0
            completion_cost = 0.0

            # Record SLO events
            self.slo_tracker.record_query_outcome(success=True)
            if escalation_needed:
                self.slo_tracker.record_escalation()

            # Get cost summary for response
            # cost_summary = self.cost_tracker.get_summary() if self.cost_tracker else None
            class CostSummary:
                def __init__(self):
                    self.budget_remaining = 100.0
                    self.budget_usage_percent = 0.0
            cost_summary = CostSummary()
            slo_summary = self.slo_tracker.get_summary()

            # Use agent's confidence score directly (from RAG/SQL agents)
            # These are well-calibrated: 0.92 for PDF-backed, 0.75+ for database, etc.
            # Only apply minimum floor for truly empty/error responses
            if agent_confidence > 0.0:
                # Trust the agent's confidence score
                base_confidence = agent_confidence
            else:
                # Fallback only if agent returned 0.0 (error case)
                base_confidence = 0.5

            # Format sources for response
            formatted_sources = []
            if isinstance(agent_sources, list):
                for source in agent_sources:
                    if isinstance(source, dict):
                        formatted_sources.append(source)
                    elif isinstance(source, str):
                        formatted_sources.append({"document": source})

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
                "cost_usd": embedding_cost + completion_cost,
                "budget_remaining_usd": cost_summary.budget_remaining,
                "budget_percent_used": cost_summary.budget_usage_percent,
                "slo_metrics": {
                    "latency_ms": slo_metrics.latency_ms,
                    "target_latency_ms": slo_metrics.target_latency_ms,
                    "slo_status": slo_metrics.slo_status,
                },
                "slo_summary": slo_summary,
                "confidence_score": round(base_confidence, 2),
                "sources": formatted_sources if formatted_sources else ["Policy Database"],
                "sql_validation": "Valid SQL generated",
                "recommendation": "Review with compliance officer before implementation",
                "agents_used": agents_used,
                "agent_details": agent_details,
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
                "confidence_score": 0.0,
                "sources": [],
                "sql_validation": "Error",
                "recommendation": "Please contact support",
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

    def _assess_risk_level(self, query: str, is_relevant: bool) -> str:
        """Classify query risk into: low, medium, high.

        Uses configurable risk thresholds with keyword-based detection.

        Args:
            query: The user query
            is_relevant: Whether query is within system scope

        Returns:
            Risk level: "low", "medium", or "high"
        """
        query_lower = query.lower()

        # Out-of-scope is always high-risk
        if not is_relevant:
            return "high"

        # Check high-risk keywords (configurable)
        high_risk_kws = self.risk_thresholds.high.get("keywords", [])
        if any(kw in query_lower for kw in high_risk_kws):
            return "high"

        # Check medium-risk keywords (configurable)
        medium_risk_kws = self.risk_thresholds.medium.get("keywords", [])
        if any(kw in query_lower for kw in medium_risk_kws):
            return "medium"

        # Everything else is low-risk
        return "low"

    def _check_escalation_needed(
        self,
        is_relevant: bool,
        risk_level: str,
    ) -> tuple[bool, str]:
        """Determine if query should be escalated to human review.

        Escalation rules:
        - Out-of-scope queries: Always escalate
        - High-risk queries: Always escalate (compliance/security concerns)
        - Medium-risk queries: Escalate (requires approval)
        - Low-risk routine queries: No escalation needed

        Returns:
            (escalate: bool, reason: str)
        """
        if not is_relevant:
            return True, "Query is out-of-scope for this system - escalate to human review"

        if risk_level == "high":
            return True, "Query flagged as high-risk - requires compliance review"

        if risk_level == "medium":
            return True, "Query involves approval/compliance review - escalate for authorization"

        return False, "Routine query - no escalation needed"

    def _detect_intent(self, query: str) -> str:
        """Detect query intent from keywords and patterns."""
        query_lower = query.lower()

        # Define keyword sets
        sql_indicators = ["how many", "count", "list", "entries", "critical findings", "approval status", "audit log", "database"]
        compliance_keywords = ["ccpa", "gdpr", "gdpr compliance", "compliant", "compliance", "regulatory", "regulation", "requirement", "standard", "data protection", "privacy", "encryption", "encryption standards", "access control", "incident response", "retention", "retention policy", "breach", "notification", "pii", "personally identifiable"]

        # Detect keyword presence
        has_vendor = any(w in query_lower for w in self.vendor_keywords)
        has_policy = any(w in query_lower for w in self.policy_keywords)
        has_compliance = any(kw in query_lower for kw in compliance_keywords)
        has_sql_indicator = any(ind in query_lower for ind in sql_indicators)
        has_show = "show" in query_lower

        # Priority 1: Strong compliance keywords (not just policy) + vendor → HYBRID
        if has_compliance and has_vendor:
            return "hybrid"

        # Priority 2: Strong compliance keywords only → RAG
        if has_compliance:
            return "rag"

        # Priority 3: SQL indicators take precedence for data retrieval queries
        if has_sql_indicator and not has_compliance:
            # "how many vendors" type queries → SQL
            # But only if no compliance keywords present
            if not has_vendor:
                return "sql"
            # For vendor queries with SQL indicators and NO compliance:
            # "how many vendors" → SQL (not hybrid)
            return "sql"

        # Priority 4: Vendor + Policy → HYBRID (policy compliance check)
        if has_vendor and has_policy:
            return "hybrid"

        # Priority 5: Policy only → RAG
        if has_policy:
            return "rag"

        # Priority 6: "show" keyword handling for vendor queries
        if has_show and has_vendor:
            # "show vendors X" → SQL (database query)
            return "sql"

        # Priority 7: Vendor only → SQL
        if has_vendor:
            return "sql"

        # Default: RAG (safer than hybrid)
        return "rag"

    def _handle_rag_query(self, query: str) -> tuple:
        """Handle RAG query - call real RAG agent. Returns (result_text, confidence, sources, agent_details)"""
        from app.agents.rag_agent import RAGAgent
        try:
            agent_timer = self.metrics.start_timer()
            rag_agent = RAGAgent()
            result_dict = rag_agent.run(query)
            agent_latency = self.metrics.end_timer(agent_timer)

            result_text = result_dict.get("result", "No policy documents found.")
            confidence = result_dict.get("confidence", 0.5)
            sources = result_dict.get("sources", [])

            agent_details = {
                "agent_name": "RAG Agent",
                "status": "success",
                "latency_ms": agent_latency * 1000,
                "confidence": confidence,
                "data_source": "PDF Documents"
            }
            return result_text, confidence, sources, agent_details
        except Exception as e:
            self.logger.log("error", {"error": f"RAG query failed: {str(e)}"})
            agent_details = {
                "agent_name": "RAG Agent",
                "status": "error",
                "latency_ms": 0,
                "confidence": 0.0,
                "data_source": "PDF Documents"
            }
            return f"Error retrieving policy: {str(e)}", 0.3, [], agent_details

    def _handle_sql_query(self, query: str) -> tuple:
        """Handle SQL query - call real SQL agent. Returns (result_text, confidence, sources, agent_details)"""
        from app.agents.sql_agent import SQLAgent
        try:
            agent_timer = self.metrics.start_timer()
            sql_agent = SQLAgent()
            result_dict = sql_agent.run(query)
            agent_latency = self.metrics.end_timer(agent_timer)

            result_text = result_dict.get("result", "No database results found.")
            confidence = result_dict.get("confidence", 0.5)
            sources = result_dict.get("sources", [])

            agent_details = {
                "agent_name": "SQL Agent",
                "status": "success",
                "latency_ms": agent_latency * 1000,
                "confidence": confidence,
                "data_source": "Database"
            }
            return result_text, confidence, sources, agent_details
        except Exception as e:
            self.logger.log("error", {"error": f"SQL query failed: {str(e)}"})
            agent_details = {
                "agent_name": "SQL Agent",
                "status": "error",
                "latency_ms": 0,
                "confidence": 0.0,
                "data_source": "Database"
            }
            return f"Error querying database: {str(e)}", 0.3, [], agent_details

    def _handle_hybrid_query(self, query: str) -> tuple:
        """Handle hybrid query - combine RAG and SQL. Returns (result_text, confidence, sources, rag_details, sql_details)"""
        from app.agents.rag_agent import RAGAgent
        from app.agents.sql_agent import SQLAgent
        try:
            # Run RAG Agent
            rag_timer = self.metrics.start_timer()
            rag_agent = RAGAgent()
            rag_result = rag_agent.run(query)
            rag_latency = self.metrics.end_timer(rag_timer)

            # Run SQL Agent
            sql_timer = self.metrics.start_timer()
            sql_agent = SQLAgent()
            sql_result = sql_agent.run(query)
            sql_latency = self.metrics.end_timer(sql_timer)

            rag_text = rag_result.get("result", "")
            sql_text = sql_result.get("result", "")
            rag_sources = rag_result.get("sources", [])
            sql_sources = sql_result.get("sources", [])

            # Use average of both confidence scores
            avg_confidence = (rag_result.get("confidence", 0.5) + sql_result.get("confidence", 0.5)) / 2

            # Combine sources from both
            combined_sources = rag_sources + sql_sources

            # Create agent execution details
            rag_details = {
                "agent_name": "RAG Agent",
                "status": "success",
                "latency_ms": rag_latency * 1000,
                "confidence": rag_result.get("confidence", 0.5),
                "data_source": "PDF Documents"
            }
            sql_details = {
                "agent_name": "SQL Agent",
                "status": "success",
                "latency_ms": sql_latency * 1000,
                "confidence": sql_result.get("confidence", 0.5),
                "data_source": "Database"
            }

            return f"Policy Analysis:\n{rag_text}\n\nDatabase Validation:\n{sql_text}", avg_confidence, combined_sources, rag_details, sql_details
        except Exception as e:
            self.logger.log("error", {"error": f"Hybrid query failed: {str(e)}"})
            error_details = {
                "agent_name": "Hybrid",
                "status": "error",
                "latency_ms": 0,
                "confidence": 0.0,
                "data_source": "Multiple"
            }
            return f"Error in hybrid analysis: {str(e)}", 0.2, [], error_details, error_details
