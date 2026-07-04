"""Escalation Agent - Determines if response requires escalation."""

from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput


class EscalationAgent(BaseAgent):
    """Determines if high-risk responses require escalation."""

    def __init__(self):
        super().__init__(name="escalation_agent", description="Escalation detector")

    async def _execute(self, agent_input: AgentInput) -> AgentOutput:
        """Determine if escalation is needed."""
        risk_result = agent_input.previous_outputs.get("risk_result", {})
        risk_level = risk_result.get("risk_level", "low")

        escalate = risk_level == "high"

        return AgentOutput(
            success=True,
            data={"escalate": escalate, "risk_level": risk_level},
            confidence=0.95,
        )
