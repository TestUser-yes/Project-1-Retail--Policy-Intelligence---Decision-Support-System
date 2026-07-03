from app.agents.intent_agent import IntentAgent
from app.agents.rag_agent import RAGAgent
from app.agents.sql_agent import SQLAgent
from app.agents.hybrid_agent import HybridAgent
from app.agents.risk_agent import RiskAgent
from app.agents.escalation_agent import EscalationAgent
from app.observability.logger import AgentLogger
from app.observability.metrics import Metrics
from app.repositories.ai_repo import AIRepository


class Orchestrator:
    def __init__(self, db):
        self.db = db
        self.intent = IntentAgent()
        self.rag = RAGAgent()
        self.sql = SQLAgent()
        self.hybrid = HybridAgent()
        self.risk = RiskAgent()
        self.escalation = EscalationAgent()
        self.logger = AgentLogger()
        self.metrics = Metrics()
        self.ai_repo = AIRepository(self.db)

    def run(self, query: str):
        try:
            self.metrics.start_timer()
            self.logger.log("input", {"query": query})

            # Step 1: Intent Detection
            try:
                intent_result = self.intent.run(query)
                self.logger.log("intent", intent_result)
                intent = intent_result.get("intent", "rag") if intent_result else "rag"
            except Exception as e:
                print(f"Intent detection failed: {e}. Using default RAG route.")
                intent = "rag"
                intent_result = {"intent": "rag", "reason": "Fallback to RAG"}

            # Step 2: Route to appropriate agent
            try:
                if intent == "rag":
                    result = self.rag.run(query)
                elif intent == "sql":
                    result = self.sql.run(query)
                else:
                    result = self.hybrid.run(query)
                self.logger.log("execution", result)
            except Exception as e:
                print(f"Route execution failed: {e}. Using fallback response.")
                result = f"Unable to process query: {str(e)}"

            # Step 3: Risk Assessment
            try:
                risk_result = self.risk.run(query, result)
                self.logger.log("risk", risk_result)
            except Exception as e:
                print(f"Risk assessment failed: {e}. Using default low risk.")
                risk_result = {"risk_level": "low", "reason": "Fallback assessment"}

            # Step 4: Escalation Decision
            try:
                escalation_result = self.escalation.run(risk_result)
            except Exception as e:
                print(f"Escalation check failed: {e}. No escalation.")
                escalation_result = {"escalate": False}

            latency = self.metrics.end_timer()

            # Step 5: Log results
            try:
                ai_record = self.ai_repo.log_query(
                    query=query,
                    intent=intent,
                    route=intent,
                    risk_level=risk_result.get("risk_level", "low"),
                    latency=latency,
                )
                self.ai_repo.log_response(
                    query_id=ai_record.id,
                    response=str(result),
                    escalate=escalation_result.get("escalate", False),
                )
            except Exception as e:
                print(f"Logging failed: {e}. Continuing without database log.")

            # Step 6: Build response
            final = {
                "query": query,
                "intent": {
                    "intent": intent_result.get("intent", "rag"),
                    "reason": intent_result.get("reason", "System default"),
                },
                "route": intent,
                "result": {
                    "result": str(result),
                },
                "risk": {
                    "risk_level": risk_result.get("risk_level", "low"),
                    "reason": risk_result.get("reason", "Default assessment"),
                },
                "escalate": escalation_result.get("escalate", False),
                "latency_seconds": latency,
            }
            self.logger.log("final", final)
            return final
        except Exception as exc:
            print(f"FATAL ERROR in orchestrator: {exc}")
            self.logger.log("error", {"error": str(exc)})
            return {
                "query": query,
                "intent": {"intent": "rag", "reason": "Error fallback"},
                "route": "rag",
                "result": {"result": f"System error: {str(exc)[:100]}"},
                "risk": {"risk_level": "low", "reason": "Error"},
                "escalate": False,
                "latency_seconds": 0,
                "error": "System failure in orchestrator",
                "details": str(exc),
            }
