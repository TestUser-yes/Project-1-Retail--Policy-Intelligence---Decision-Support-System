from app.llm import LLMService

llm = LLMService()


class RiskAgent:
    def run(self, query: str, result: dict):
        return llm.generate_json([
            {
                "role": "system",
                "content": """You are a Risk Evaluation Agent.

Return:
{
  "risk_level": "low|medium|high",
  "reason": ""
}"""
            },
            {
                "role": "user",
                "content": f"Query: {query}\nResult: {result}"
            }
        ])
