# app/llm.py

import os
import json
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class LLMService:
    """
    Core LLM Brain for Retail Policy AI System.

    This replaces rule-based classification with AI reasoning.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    # ---------------------------------------------------------
    # 1. BASIC CHAT INTERFACE (for debugging / fallback)
    # ---------------------------------------------------------
    def chat(self, messages, temperature: float = 0.2):
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content

    # ---------------------------------------------------------
    # 2. STRUCTURED JSON GENERATOR (CORE FUNCTION)
    # ---------------------------------------------------------
    def generate_json(self, messages, temperature: float = 0.2):
        """
        Forces LLM to return valid JSON output
        """
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content

        try:
            return json.loads(content)
        except Exception:
            return {
                "error": "Invalid JSON response from LLM",
                "raw_output": content
            }

    # ---------------------------------------------------------
    # 3. INTENT + ROUTING BRAIN (MOST IMPORTANT PART)
    # ---------------------------------------------------------
    def analyze_query(self, query: str):
        """
        Replaces classifier.py completely.

        This function decides:
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
- "rag" → policy questions, text-based knowledge, compliance docs
- "sql" → structured data queries (vendors, audits, records)
- "hybrid" → needs both database + policy reasoning

RISK LEVELS:
- low → informational queries
- medium → policy-sensitive queries
- high → compliance / legal / audit risk

OUTPUT FORMAT (STRICT JSON ONLY):
{
  "intent": "rag | sql | hybrid",
  "risk_level": "low | medium | high",
  "confidence": 0.0-1.0,
  "reason": "short explanation"
}
"""
            },
            {
                "role": "user",
                "content": query
            }
        ]

        return self.generate_json(messages)

    # ---------------------------------------------------------
    # 4. ESCALATION DECISION ENGINE (future-ready)
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
