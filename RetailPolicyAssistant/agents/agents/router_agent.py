"""Route selection agent."""

from app.agents.intent_agent import Intent


def select_route(intent: Intent) -> str:
    if intent == Intent.SQL:
        return "sql"
    if intent == Intent.HYBRID:
        return "hybrid"
    return "rag"
