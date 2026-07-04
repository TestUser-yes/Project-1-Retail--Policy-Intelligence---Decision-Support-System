"""Confidence Agent - Multi-factor confidence scoring."""

from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput

class ConfidenceAgent(BaseAgent):
    """Calculates multi-factor confidence score."""

    def __init__(self):
        super().__init__(name="confidence_agent", description="Confidence scorer")

    async def _execute(self, agent_input: AgentInput) -> AgentOutput:
        """Calculate confidence."""
        previous = agent_input.previous_outputs
        
        doc_confidence = previous.get("document_confidence", 0.0)
        sql_confidence = previous.get("sql_confidence", 0.0)
        reflection_confidence = previous.get("reflection_confidence", 0.0)
        agreement_confidence = previous.get("agreement_confidence", 0.0)
        
        final_confidence = (
            doc_confidence * 0.4 +
            sql_confidence * 0.2 +
            reflection_confidence * 0.2 +
            agreement_confidence * 0.2
        )

        return AgentOutput(
            success=True,
            data={"confidence": final_confidence},
            confidence=final_confidence,
        )
