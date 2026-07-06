import json

import requests

from app.core import settings

from .base import BaseLLM


class OllamaLLM(BaseLLM):
    def __init__(self, model="phi3:mini"):
        self.model = model

    def chat(self, messages, temperature=0.2):
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

    def generate_json(self, messages, temperature=0.2):
        content = self.chat(messages, temperature)
        try:
            return json.loads(content)
        except Exception:
            return {"error": "Invalid JSON", "raw_output": content}

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
