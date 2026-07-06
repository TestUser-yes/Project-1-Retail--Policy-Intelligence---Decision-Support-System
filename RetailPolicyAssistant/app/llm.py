import json

import requests

from app.core import settings


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
        url = f"{settings.OLLAMA_BASE_URL}/api/chat"
        payload = {
            "model": self.model or settings.OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": 512,
            },
        }
        response = requests.post(
            url,
            json=payload,
            timeout=300,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]

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
    # 4. RAG ANSWER GENERATION (with standardized templates)
    # ---------------------------------------------------------
    def generate_rag_answer(self, question: str, context: str, template_pattern: str = "basic"):
        """Generate a grounded answer using retrieved policy context.

        Uses standardized RAG templates from app.prompts (single source of truth).

        Args:
            question: User's actual query
            context: Retrieved documents from retrieval pipeline
            template_pattern: Which RAG template to use:
                - "basic" (default): Simple instructions with context + question
                - "strict_grounding": Prevents hallucinations with explicit fallback
                - "structured_citation": Includes source citations
                - "multi_chunk_synthesis": Combines multiple chunks

        Returns:
            LLM response text

        Raises:
            ValueError: If context or question is empty
            KeyError: If template_pattern not found
        """
        if not context or not context.strip():
            raise ValueError("Context cannot be empty for RAG generation")
        if not question or not question.strip():
            raise ValueError("Question cannot be empty for RAG generation")

        from app.prompts import get_rag_template

        template = get_rag_template(template_pattern)

        # Debug logging
        print("\n" + "=" * 60)
        print(f"RAG GENERATION STARTED")
        print(f"Template Pattern: {template.get_name()}")
        print(f"Context Length: {len(context)} characters")
        print(f"Question: {question}")
        print("=" * 60)

        # Format message using template
        messages = template.format_prompt(context, question)

        print("\nDEBUG: Retrieved Context (first 500 chars):")
        print(context[:500] + "..." if len(context) > 500 else context)
        print("\n" + "=" * 60)

        try:
            response = self.chat(messages)
            print(f"LLM Response Length: {len(response)} characters")
            print("=" * 60 + "\n")
            return response
        except Exception as e:
            print(f"\nRAG GENERATION ERROR: {e}")
            print("=" * 60 + "\n")
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
