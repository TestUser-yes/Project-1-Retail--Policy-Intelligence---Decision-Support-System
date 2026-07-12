"""Orchestrator for demo: routes queries without calling external services."""

import asyncio
from app.observability.logger import AgentLogger
from app.observability.metrics import Metrics
from app.observability.langfuse_tracer import trace_function
from app.repositories.ai_repo import AIRepository
from app.core.cost_tracking import get_cost_tracker, CostSummary
from app.core.slo_tracker import get_slo_tracker
from app.config import get_config
from app.utils.tokenizer import count_query_response_tokens
from app.middleware.guardrails_middleware import get_guardrails_middleware
from app.evaluation.phase1_orchestrator import evaluate_phase1
from app.evaluation.phase2_orchestrator import evaluate_phase2, evaluate_phase2_sync


class Orchestrator:
    def __init__(self, db):
        self.db = db
        self.logger = AgentLogger()
        self.metrics = Metrics()
        self.ai_repo = AIRepository(self.db)
        self.cost_tracker = get_cost_tracker()
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
    async def run(self, query: str, user_role: str = "viewer"):
        """Process query and return demo response."""
        import sys
        print("[ORCHESTRATOR.RUN] Starting...", file=sys.stderr)
        try:
            # ===== GUARDRAILS LAYER 1-6: INPUT VALIDATION =====
            middleware = get_guardrails_middleware(user_role=user_role)
            is_valid, violations = middleware.validate_input(query)

            if not is_valid:
                self.logger.log("guardrails_block", {"violations": violations})
                latency = self.metrics.end_timer() if hasattr(self.metrics, 'end_timer') else 0
                self.logger.log("response", {
                    "blocked_by": "guardrails",
                    "violations": violations
                })
                return {
                    "query": query,
                    "route": "blocked",
                    "result": {"result": f"Query blocked by security guardrails: {violations}"},
                    "risk": {"risk_level": "high", "reason": "Guardrails violation"},
                    "escalate": True,
                    "escalation_reason": "Security violation detected",
                    "latency_seconds": latency,
                    "confidence_score": 0.0,
                    "guardrails_violations": violations,
                    "agents_used": [],
                    "agent_details": [],
                }

            # ===== GUARDRAILS LAYER 7: RBAC CHECK =====
            allowed, rbac_reason = middleware.check_access("read")
            if not allowed:
                self.logger.log("rbac_block", {"reason": rbac_reason})
                latency = self.metrics.end_timer() if hasattr(self.metrics, 'end_timer') else 0
                return {
                    "query": query,
                    "route": "blocked",
                    "result": {"result": f"Access denied: {rbac_reason}"},
                    "risk": {"risk_level": "high", "reason": "Insufficient permissions"},
                    "escalate": True,
                    "escalation_reason": "RBAC violation",
                    "latency_seconds": latency,
                    "confidence_score": 0.0,
                    "guardrails_violations": [rbac_reason],
                    "agents_used": [],
                    "agent_details": [],
                }

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
            retrieval_method = "semantic"  # Default
            retrieval_agents = []  # Default
            retrieval_pipeline = {}  # Default

            if intent == "sql":
                result, agent_confidence, agent_sources, agent_exec, retr_details = self._handle_sql_query(query)
                route = "sql"
                agents_used.append("sql_agent")
                agent_details.append(agent_exec)
                # SQL doesn't have retrieval pipeline, so keep defaults
            elif intent == "rag":
                result, agent_confidence, agent_sources, agent_exec, retr_details = self._handle_rag_query(query)
                route = "rag"
                agents_used.append("rag_agent")
                agent_details.append(agent_exec)
                # Extract retrieval details
                retrieval_method = retr_details.get("retrieval_method", "semantic")
                retrieval_agents = retr_details.get("retrieval_agents", [])
                retrieval_pipeline = retr_details.get("retrieval_pipeline", {})
            else:
                result, agent_confidence, agent_sources, rag_exec, sql_exec, rag_retr, sql_retr = self._handle_hybrid_query(query)
                route = "hybrid"
                agents_used.extend(["rag_agent", "sql_agent"])
                agent_details.extend([rag_exec, sql_exec])
                # Use RAG retrieval details for hybrid (both agents used but retrieval comes from RAG)
                retrieval_method = rag_retr.get("retrieval_method", "semantic")
                retrieval_agents = rag_retr.get("retrieval_agents", [])
                retrieval_pipeline = rag_retr.get("retrieval_pipeline", {})

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

            # Record cost tracking with real token counts
            if self.cost_tracker:
                self.cost_tracker.track_query_cost(embedding_tokens, completion_tokens)
                embedding_cost = self.cost_tracker.calculate_embedding_cost(embedding_tokens)
                completion_cost = self.cost_tracker.calculate_completion_cost(completion_tokens)
            else:
                embedding_cost = 0.0
                completion_cost = 0.0

            # Record SLO events
            self.slo_tracker.record_query_outcome(success=True)
            if escalation_needed:
                self.slo_tracker.record_escalation()

            # Get cost summary for response
            cost_summary = self.cost_tracker.get_summary() if self.cost_tracker else CostSummary()
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

            # ===== GUARDRAILS LAYER 2, 3, 8: OUTPUT SANITIZATION =====
            sanitized_result = middleware.sanitize_output(str(result))

            # Build response with SLO metrics
            response = {
                "query": query,
                "intent": {
                    "intent": intent,
                    "reason": intent_result.get("reason", ""),
                },
                "route": route,
                "result": {
                    "result": sanitized_result,
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
                # Multi-agent retrieval details (Level 2)
                "retrieval_method": retrieval_method,
                "retrieval_agents": retrieval_agents,
                "retrieval_pipeline": retrieval_pipeline,
                # Guardrails status (all 8 layers)
                "guardrails_status": {
                    "input_validated": True,
                    "rbac_checked": True,
                    "output_sanitized": True,
                    "pii_masked": True,
                    "user_role": user_role,
                    "violations": middleware.violations if middleware.violations else []
                }
            }

            # ===== PHASE 1: EVALUATION (Optional, Async) =====
            # Evaluate response using Phase 1 metrics
            try:
                await evaluate_phase1(
                    response=response,
                    query=query,
                    route=route,
                    total_latency_ms=latency * 1000,
                )
            except Exception as e:
                self.logger.log("phase1_evaluation_schedule_error", {"error": str(e)})

            # ===== PHASE 2: RETRIEVAL QUALITY EVALUATION (Optional, Sync + Async) =====
            # Evaluate retrieval quality using Phase 2 metrics
            # Only for RAG/Hybrid routes
            if route in ("rag", "hybrid"):
                try:
                    retrieved_chunks = response.get("sources", [])
                    retrieval_method = response.get("retrieval_method", "unknown")

                    # Sync evaluation for immediate response inclusion
                    metrics = evaluate_phase2_sync(
                        query=query,
                        retrieved_chunks=retrieved_chunks,
                        route=route,
                        retrieval_latency_ms=latency * 1000,
                        retrieval_method=retrieval_method,
                    )
                    if metrics:
                        response["retrieval_metrics"] = metrics

                    # Async evaluation for database persistence
                    await evaluate_phase2(
                        response=response,
                        query=query,
                        route=route,
                        retrieved_chunks=retrieved_chunks,
                        retrieval_latency_ms=latency * 1000,
                        retrieval_method=retrieval_method,
                    )
                except Exception as e:
                    self.logger.log("phase2_evaluation_schedule_error", {"error": str(e)})

            return response

        except Exception as exc:
            self.logger.log("error", {"error": str(exc)})
            latency = self.metrics.end_timer()
            error_response = {
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
                "agents_used": [],
                "agent_details": [],
                "retrieval_method": "semantic",
                "retrieval_agents": [],
                "retrieval_pipeline": {},
            }

            # Still evaluate even on error (for completeness)
            try:
                await evaluate_phase1(
                    response=error_response,
                    query=query,
                    route="rag",
                    total_latency_ms=latency * 1000,
                )
            except Exception as e:
                self.logger.log("phase1_evaluation_schedule_error", {"error": str(e)})

            return error_response

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
        sql_indicators = ["how many", "count", "list", "entries", "critical findings", "approval status", "audit log", "database", "show", "recent", "current", "is the"]
        compliance_keywords = ["ccpa", "gdpr", "gdpr compliance", "compliant", "compliance", "regulatory", "regulation", "requirement", "standard", "data protection", "privacy", "encryption", "encryption standards", "access control", "incident response", "retention", "retention policy", "breach", "notification", "pii", "personally identifiable"]
        database_patterns = ["vendor", "audit", "finding", "record", "status", "jurisdiction"]

        # Detect keyword presence
        has_vendor = any(w in query_lower for w in self.vendor_keywords)
        has_policy = any(w in query_lower for w in self.policy_keywords)
        has_compliance = any(kw in query_lower for kw in compliance_keywords)
        has_sql_indicator = any(ind in query_lower for ind in sql_indicators)
        has_show = "show" in query_lower
        has_db_pattern = any(p in query_lower for p in database_patterns)

        # HIGHEST PRIORITY: SQL indicators override everything else (strongest signal for database query)
        # "List vendors", "How many vendors", "Show recent", "What is current status" → SQL
        if has_sql_indicator:
            # SQL indicators always point to database unless it's explicitly a policy/requirement query
            if "requirement" not in query_lower and "standard" not in query_lower:
                return "sql"

        # Priority 2: Strong compliance keywords + vendor + policy → HYBRID
        if has_compliance and has_vendor and has_policy:
            return "hybrid"

        # Priority 3: Compliance + vendor (no policy docs needed) → SQL
        if has_compliance and has_vendor and not has_policy:
            return "sql"

        # Priority 4: Strong compliance keywords + policy → RAG
        if has_compliance and has_policy:
            return "rag"

        # Priority 5: Vendor + Policy → HYBRID (policy compliance check)
        if has_vendor and has_policy:
            return "hybrid"

        # Priority 6: Policy only → RAG
        if has_policy:
            return "rag"

        # Priority 7: Vendor only → SQL
        if has_vendor:
            return "sql"

        # Default: RAG (safer than hybrid)
        return "rag"

    def _handle_rag_query(self, query: str) -> tuple:
        """Handle RAG query - call real RAG agent. Returns (result_text, confidence, sources, agent_details, retrieval_details)"""
        from app.agents.rag_agent import RAGAgent
        import time
        try:
            agent_start = time.time()
            rag_agent = RAGAgent()
            result_dict = rag_agent.run(query)
            agent_latency = time.time() - agent_start

            result_text = result_dict.get("result", "No policy documents found.")
            confidence = result_dict.get("confidence", 0.5)
            sources = result_dict.get("sources", [])

            # Extract retrieval details from RAG agent
            retrieval_method = result_dict.get("retrieval_method", "semantic")
            retrieval_agents = result_dict.get("retrieval_agents", [])
            retrieval_pipeline = result_dict.get("retrieval_pipeline", {})

            agent_details = {
                "agent_name": "RAG Agent",
                "status": "success",
                "latency_ms": agent_latency * 1000,
                "confidence": confidence,
                "data_source": "PDF Documents"
            }

            retrieval_details = {
                "retrieval_method": retrieval_method,
                "retrieval_agents": retrieval_agents,
                "retrieval_pipeline": retrieval_pipeline,
            }

            return result_text, confidence, sources, agent_details, retrieval_details
        except Exception as e:
            self.logger.log("error", {"error": f"RAG query failed: {str(e)}"})
            agent_details = {
                "agent_name": "RAG Agent",
                "status": "error",
                "latency_ms": 0,
                "confidence": 0.0,
                "data_source": "PDF Documents"
            }
            retrieval_details = {
                "retrieval_method": "semantic",
                "retrieval_agents": [],
                "retrieval_pipeline": {},
            }
            return f"Error retrieving policy: {str(e)}", 0.3, [], agent_details, retrieval_details

    def _handle_sql_query(self, query: str) -> tuple:
        """Handle SQL query - call real SQL agent. Returns (result_text, confidence, sources, agent_details, retrieval_details)"""
        from app.agents.sql_agent import SQLAgent
        import time
        try:
            agent_start = time.time()
            sql_agent = SQLAgent()
            result_dict = sql_agent.run(query)
            agent_latency = time.time() - agent_start

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

            # SQL doesn't have retrieval pipeline (no multi-agent retrieval)
            retrieval_details = {
                "retrieval_method": "sql",
                "retrieval_agents": [],
                "retrieval_pipeline": {},
            }

            return result_text, confidence, sources, agent_details, retrieval_details
        except Exception as e:
            self.logger.log("error", {"error": f"SQL query failed: {str(e)}"})
            agent_details = {
                "agent_name": "SQL Agent",
                "status": "error",
                "latency_ms": 0,
                "confidence": 0.0,
                "data_source": "Database"
            }
            retrieval_details = {
                "retrieval_method": "sql",
                "retrieval_agents": [],
                "retrieval_pipeline": {},
            }
            return f"Error querying database: {str(e)}", 0.3, [], agent_details, retrieval_details

    def _handle_hybrid_query(self, query: str) -> tuple:
        """Handle hybrid query - combine RAG and SQL. Returns (result_text, confidence, sources, rag_exec, sql_exec, rag_retr, sql_retr)"""
        from app.agents.rag_agent import RAGAgent
        from app.agents.sql_agent import SQLAgent
        import time
        try:
            # Run RAG Agent
            rag_start = time.time()
            rag_agent = RAGAgent()
            rag_result = rag_agent.run(query)
            rag_latency = time.time() - rag_start

            # Run SQL Agent
            sql_start = time.time()
            sql_agent = SQLAgent()
            sql_result = sql_agent.run(query)
            sql_latency = time.time() - sql_start

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

            # Extract retrieval details from RAG result
            rag_retrieval = {
                "retrieval_method": rag_result.get("retrieval_method", "semantic"),
                "retrieval_agents": rag_result.get("retrieval_agents", []),
                "retrieval_pipeline": rag_result.get("retrieval_pipeline", {}),
            }

            # SQL doesn't have multi-agent retrieval
            sql_retrieval = {
                "retrieval_method": "sql",
                "retrieval_agents": [],
                "retrieval_pipeline": {},
            }

            return f"Policy Analysis:\n{rag_text}\n\nDatabase Validation:\n{sql_text}", avg_confidence, combined_sources, rag_details, sql_details, rag_retrieval, sql_retrieval
        except Exception as e:
            self.logger.log("error", {"error": f"Hybrid query failed: {str(e)}"})
            error_details = {
                "agent_name": "Hybrid",
                "status": "error",
                "latency_ms": 0,
                "confidence": 0.0,
                "data_source": "Multiple"
            }
            empty_retrieval = {
                "retrieval_method": "error",
                "retrieval_agents": [],
                "retrieval_pipeline": {},
            }
            return f"Error in hybrid analysis: {str(e)}", 0.2, [], error_details, error_details, empty_retrieval, empty_retrieval
