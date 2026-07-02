import os

from .ollama_llm import OllamaLLM


class LLMService(OllamaLLM):

    def __init__(self):
        model = os.getenv("OLLAMA_MODEL", "phi3:mini")
        super().__init__(model=model)

    # ---------------------------------------------------------
    # INTENT + ROUTING BRAIN
    # ---------------------------------------------------------
    def analyze_query(self, query: str):

        messages = [
            {
                "role": "system",
                "content": """
You are an enterprise AI decision engine for a Retail Policy System.

Return ONLY valid JSON.

ROUTING RULES:
- rag -> policy questions
- sql -> structured database questions
- hybrid -> requires both

RISK LEVELS:
- low
- medium
- high

Return JSON only:

{
  "intent": "rag | sql | hybrid",
  "risk_level": "low | medium | high",
  "confidence": 0.0,
  "reason": ""
}
"""
            },
            {
                "role": "user",
                "content": query
            }
        ]

        try:
            result = self.generate_json(messages)

            if isinstance(result, dict) and "error" not in result:
                return result

        except Exception:
            pass

        return self._fallback_analyze_query(query)

    def _fallback_analyze_query(self, query: str):

        text = query.lower()

        sql_terms = {
            "show",
            "list",
            "get",
            "fetch",
            "find",
            "approval status",
            "audit log",
            "vendor id",
            "record id",
            "database",
        }

        policy_terms = {
            "policy",
            "section",
            "clause",
            "compliance",
            "allowed",
        }

        policy_keywords = {
            "policy",
            "bribery",
            "compliance",
            "allowed",
            "gift",
            "ethics",
            "conduct",
        }

        high_risk = {
            "bribery",
            "gift",
            "legal",
            "investigation",
            "cross-border",
        }

        needs_sql = any(x in text for x in sql_terms)
        needs_policy = any(x in text for x in policy_terms)

        if any(word in text for word in policy_keywords):
            intent = "rag"
        elif needs_sql and needs_policy:
            intent = "hybrid"
        elif needs_sql:
            intent = "sql"
        else:
            intent = "rag"

        if any(x in text for x in high_risk):
            risk = "high"
        elif intent == "hybrid" or needs_policy:
            risk = "medium"
        else:
            risk = "low"

        confidence = (
            0.92 if intent == "hybrid"
            else 0.88 if intent == "sql"
            else 0.81
        )

        return {
            "intent": intent,
            "risk_level": risk,
            "confidence": confidence,
            "reason": "Local heuristic",
        }

    # ---------------------------------------------------------
    # ESCALATION
    # ---------------------------------------------------------
    def should_escalate(self, risk_level, confidence):

        if risk_level == "high":
            return True

        if risk_level == "medium" and confidence < 0.7:
            return True

        return False