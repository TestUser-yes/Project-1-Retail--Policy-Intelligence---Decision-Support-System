from app.models.ai_queries import AIQuery
from app.models.ai_response import AIResponse


class AIRepository:
    def __init__(self, db):
        self.db = db

    def log_query(self, query: str, intent: str, route: str, risk_level: str, latency: float):
        record = AIQuery(
            query=query,
            intent=intent,
            route=route,
            risk_level=risk_level,
            latency=latency,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def log_response(self, query_id: int, response: str, escalate: bool):
        record = AIResponse(
            query_id=query_id,
            response=response,
            escalate=escalate,
        )
        self.db.add(record)
        self.db.commit()
        return record
