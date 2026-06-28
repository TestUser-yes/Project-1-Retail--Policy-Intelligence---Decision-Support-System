from app.llm import LLMService

llm = LLMService()


class IntentAgent:
    """
    Understands user intent deeply
    """

    def run(self, query: str):
        return llm.generate_json([
            {
                "role": "system",
                "content": """
You are an Intent Detection Agent.

Classify the query into:
- rag
- sql
- hybrid

Return JSON:
{
  "intent": "",
  "reason": ""
}
"""
            },
            {
                "role": "user",
                "content": query
            }
        ])