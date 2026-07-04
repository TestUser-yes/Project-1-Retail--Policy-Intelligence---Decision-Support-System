"""Response Agent - Formats final response."""

from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput

class ResponseAgent(BaseAgent):
    """Formats and delivers final response with metadata."""

    def __init__(self):
        super().__init__(name="response_agent", description="Response formatter")

    async def _execute(self, agent_input: AgentInput) -> AgentOutput:
        """Format response."""
        previous = agent_input.previous_outputs
        
        formatted_response = {
            "response": previous.get("answer", ""),
            "confidence": previous.get("confidence", 0.0),
            "sources": previous.get("sources", []),
            "risk_level": previous.get("risk_level", "LOW"),
        }

        return AgentOutput(
            success=True,
            data=formatted_response,
            confidence=previous.get("confidence", 0.5),
        )
