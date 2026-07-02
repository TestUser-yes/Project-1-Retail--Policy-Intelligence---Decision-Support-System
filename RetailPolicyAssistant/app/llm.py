import json
import ollama


class LLMService:
    """
    Core LLM Brain for the Retail Policy AI System.

    The main flow uses the LLM first, and falls back to a local
    heuristic only when the Ollama call is unavailable.
    """

    def __init__(self, model: str = "phi3:mini"):
        self.model = model

    # ---------------------------------------------------------
    # 1. BASIC CHAT INTERFACE (for debugging / fallback)
    # ---------------------------------------------------------
    def chat(self, messages, temperature: float = 0.2):
        response = ollama.chat(
            model=self.model,
            messages=messages,
            options={
                "temperature": temperature,
            },
        )
        return response["message"]["content"]

    # ---------------------------------------------------------
    # 2. STRUCTURED JSON GENERATOR (CORE FUNCTION)
    # ---------------------------------------------------------
    def generate_json(self, messages, temperature: float = 0.2):
        content = self.chat(messages, temperature)
        try:
            return json.loads(content)
        except Exception:
            return {
                "error": "Invalid JSON",
                "raw_output": content,
            }

    # ---------------------------------------------------------
    # 3. INTENT + ROUTING BRAIN (MOST IMPORTANT PART)
    # ---------------------------------------------------------
    def analyze_query(self, query: str):
        """
        Decide:
        - intent (rag / sql / hybrid)
        - risk level
        - confidence
        - reasoning
        """

        messages = [
            {
                "role": "system",
                "content": """
You are an enterprise AI decision engine for a Retail Policy System.

Your job:
1. Understand the user query
2. Decide how to process it
3. Return ONLY valid JSON

ROUTING RULES:
- "rag" -> policy questions, text-based knowledge, compliance docs
- "sql" -> structured data queries (vendors, audits, records)
- "hybrid" -> needs both database + policy reasoning

RISK LEVELS:
- low -> informational queries
- medium -> policy-sensitive queries
- high -> compliance / legal / audit risk

OUTPUT FORMAT (STRICT JSON ONLY):
{
  "intent": "rag | sql | hybrid",
  "risk_level": "low | medium | high",
  "confidence": 0.0-1.0,
  "reason": "short explanation"
}
""",
            },
            {
                "role": "user",
                "content": query,
            },
        ]

        try:
            decision = self.generate_json(messages)
            if isinstance(decision, dict) and "error" not in decision:
                return decision
        except Exception:
            pass

        return self._fallback_analyze_query(query)

    def _fallback_analyze_query(self, query: str):
        text = query.lower()

        sql_terms = {
            "vendor",
            "vendors",
            "approval status",
            "audit log",
            "retention record",
            "records",
            "record id",
            "database",
        }
        policy_terms = {
            "policy",
            "clause",
            "section",
            "explain",
            "allowed",
            "compliance",
            "compliant",
        }
        high_risk_terms = {
            "cross-border",
            "restricted jurisdiction",
            "legal hold",
            "critical-risk",
            "bribery",
            "gift",
            "hospitality",
            "overseas supplier",
            "audit finding",
            "unresolved",
            "legal validation",
            "lawsuit",
            "investigation",
        }

        needs_sql = any(term in text for term in sql_terms)
        needs_policy = any(term in text for term in policy_terms)

        if needs_sql and needs_policy:
            intent = "hybrid"
        elif needs_sql:
            intent = "sql"
        else:
            intent = "rag"

        if any(term in text for term in high_risk_terms):
            risk_level = "high"
        elif needs_policy or intent == "hybrid":
            risk_level = "medium"
        else:
            risk_level = "low"

        confidence = 0.92 if intent == "hybrid" else 0.88 if intent == "sql" else 0.81

        return {
            "intent": intent,
            "risk_level": risk_level,
            "confidence": confidence,
            "reason": "Local fallback analysis used because the OpenAI response was unavailable.",
        }

    # ---------------------------------------------------------
    # 4. RAG ANSWER GENERATION
    # ---------------------------------------------------------
    def generate_rag_answer(self, question: str, context: str):
        """
        Generate a grounded answer using retrieved policy context.
        """
        messages = [
            {
                "role": "system",
                "content": """You are an enterprise Retail Policy Assistant.
Answer ONLY using the supplied policy context.
Rules:
- Never invent information.
- If the answer is not in the context, say: "I couldn't find that information in the available policy documents."
- Keep answers concise and professional.
- Mention policy names only if relevant.""",
            },
            {
                "role": "user",
                "content": f"""Policy Context:{context}
----------------------------
Question:{question}""",
            },
        ]
        try:
            return self.chat(messages)
        except Exception as e:
            print("\nLLM ERROR:")
            print(e)
            raise

    # ---------------------------------------------------------
    # 5. ESCALATION DECISION ENGINE (future-ready)
    # ---------------------------------------------------------
    def should_escalate(self, risk_level: str, confidence: float):
        """
        Simple but extensible escalation logic
        """

        if risk_level == "high":
            return True

        if risk_level == "medium" and confidence < 0.7:
            return True

        return False
