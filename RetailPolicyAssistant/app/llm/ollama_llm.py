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

    def generate_rag_answer(self, question, context):
        messages = [
            {
                "role": "system",
                "content": """
You are an enterprise Retail Policy Assistant.
You MUST answer ONLY from the supplied context.
IMPORTANT RULES
1. Never use any outside knowledge.
2. Never infer missing information.
3. Never complete broken tables.
4. Never guess policy values.
5. Never guess approvals.
6. Never rewrite numbers.
7. Never rewrite currency.
8. If multiple chunks disagree, state exactly what each chunk says.
9. If information is incomplete because the table is split, reply exactly:
"I couldn't find that information in the provided policy documents."
10. Quote the exact sentence before explaining.
11. At the end write
Source:DocumentPage
""",
            },
            {
                "role": "user",
                "content": f"""Below is the ONLY policy context you may use.
=====================POLICY CONTEXT=====================
{context}
=====================QUESTION=====================
{question}
Remember:Never answer using anything outside the policy context.""",
            },
        ]
        return self.chat(messages)
