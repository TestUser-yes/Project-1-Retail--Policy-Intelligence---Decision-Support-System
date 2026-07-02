import json

import ollama

from .base import BaseLLM


class OllamaLLM(BaseLLM):
    def __init__(self, model="phi3:mini"):
        self.model = model

    def chat(self, messages, temperature=0.2):
        response = ollama.chat(
            model=self.model,
            messages=messages,
            options={"temperature": temperature},
        )
        return response["message"]["content"]

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
                "content": """You are an enterprise Retail Policy Assistant.
Answer ONLY using the supplied policy context.
Rules:
- Never invent information.
- If the answer is not present, say you couldn't find it.
- Keep answers concise.""",
            },
            {
                "role": "user",
                "content": f"""Policy Context:{context}
Question:{question}""",
            },
        ]
        return self.chat(messages)
