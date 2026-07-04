"""Reflection Agent - Self-correction and quality checking."""

from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput

class ReflectionAgent(BaseAgent):
    """Performs self-reflection on generated answer."""

    def __init__(self):
        super().__init__(name="reflection_agent", description="Self-reflection engine")

    async def _execute(self, agent_input: AgentInput) -> AgentOutput:
        """Reflect on answer quality."""
        answer = agent_input.previous_outputs.get("answer", "")
        docs = agent_input.previous_outputs.get("documents", [])
        
        checks = {
            "answers_question": bool(answer),
            "has_citations": len(docs) > 0,
            "complete": len(answer) > 50,
            "contradictions": False,
        }
        
        passed_checks = sum(1 for v in checks.values() if v)
        confidence = passed_checks / len(checks)
        
        return AgentOutput(
            success=True,
            data={"checks": checks, "confidence": confidence},
            confidence=confidence,
        )
