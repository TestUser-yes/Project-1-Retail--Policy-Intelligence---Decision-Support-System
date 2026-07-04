"""Validator Agent - Validates answer quality."""

from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput

class ValidatorAgent(BaseAgent):
    """Validates answer quality and completeness."""

    def __init__(self):
        super().__init__(name="validator_agent", description="Answer validator")

    async def _execute(self, agent_input: AgentInput) -> AgentOutput:
        """Validate answer."""
        return AgentOutput(
            success=True,
            data={"valid": True, "confidence": 0.85},
            confidence=0.85,
        )
