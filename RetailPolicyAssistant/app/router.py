# app/router.py

from app.llm import LLMService

llm = LLMService()

def route_query(query: str):
    """
    AI-driven router
    """
    decision = llm.analyze_query(query)
    intent = decision.get("intent", "rag")
    risk = decision.get("risk_level", "low")
    confidence = decision.get("confidence", 0.5)
    return {
        "intent": intent,
        "risk_level": risk,
        "confidence": confidence,
        "reason": decision.get("reason", ""),
        "escalate": llm.should_escalate(risk, confidence)
    }
