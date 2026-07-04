"""Router Agent - Routes queries to appropriate execution path."""

from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.llm import LLMService

llm = LLMService()


class RouterAgent(BaseAgent):
    """Routes queries to RAG, SQL, or Hybrid execution path."""

    def __init__(self):
        super().__init__(name="router_agent", description="Query router")

    async def _execute(self, agent_input: AgentInput) -> AgentOutput:
        """Route query to appropriate execution path."""
        intent = agent_input.previous_outputs.get("intent", "rag")

        route_decision = {
            "route": intent,
            "decision": f"Routed to {intent.upper()} execution path"
        }

        return AgentOutput(
            success=True,
            data=route_decision,
            confidence=0.9,
        )