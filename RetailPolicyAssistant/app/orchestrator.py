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

            intent_result = self.intent.run(query)
            self.logger.log("intent", intent_result)
            intent = intent_result.get("intent", "rag")

            if intent == "rag":
                result = self.rag.run(query)
            elif intent == "sql":
                result = self.sql.run(query)
            else:
                result = self.hybrid.run(query)
            self.logger.log("execution", result)

            risk_result = self.risk.run(query, result)
            self.logger.log("risk", risk_result)

            escalation_result = self.escalation.run(risk_result)
            latency = self.metrics.end_timer()

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
                escalate=escalation_result["escalate"],
            )

            final = {
                "query": query,
                "intent": {
                    "intent": intent_result.get("intent"),
                    "reason": intent_result.get("reason"),
                },
                "route": intent,
                "result": {
                    "result": str(result),
                },
                "risk": {
                    "risk_level": risk_result.get("risk_level"),
                    "reason": risk_result.get("reason"),
                },
                "escalate": escalation_result["escalate"],
                "latency": latency,
            }
            self.logger.log("final", final)
            return final
        except Exception as exc:
            self.logger.log("error", {"error": str(exc)})
            return {
                "error": "System failure in orchestrator",
                "details": str(exc),
            }
