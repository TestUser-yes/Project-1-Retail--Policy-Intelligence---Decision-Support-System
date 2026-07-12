"""Intent Agent - Detects user intent (RAG, SQL, Hybrid)."""

from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.llm import LLMService

llm = LLMService()


class IntentAgent(BaseAgent):
    """Detects user intent: RAG, SQL, or Hybrid."""

    def __init__(self):
        super().__init__(name="intent_agent", description="Intent detector")

    async def _execute(self, agent_input: AgentInput) -> AgentOutput:
        """Detect query intent."""
        query = agent_input.query

        try:
            result = llm.generate_json([
                {
                    "role": "system",
                    "content": "You are an Intent Detection Agent. Classify the query into: rag, sql, or hybrid. Return JSON: {\"intent\": \"\", \"reason\": \"\"}"
                },
                {
                    "role": "user",
                    "content": query
                }
            ])

            intent = result.get("intent", "hybrid")
            confidence = 0.85 if intent in ["rag", "sql", "hybrid"] else 0.5

            return AgentOutput(
                success=True,
                data=result,
                confidence=confidence,
            )
        except Exception as e:
            return AgentOutput(
                success=False,
                error=str(e),
                confidence=0.0,
            )