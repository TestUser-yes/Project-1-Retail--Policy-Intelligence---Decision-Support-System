"""Validator Agent - Validates answer quality and completeness."""

from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.llm import LLMService
import json


class ValidatorAgent(BaseAgent):
    """Validates answer quality, completeness, and relevance."""

    def __init__(self):
        super().__init__(name="validator_agent", description="Answer quality validator")
        self.llm = LLMService()

    async def _execute(self, agent_input: AgentInput) -> AgentOutput:
        """Validate answer quality using LLM."""
        try:
            query = agent_input.get("query", "")
            answer = agent_input.get("answer", "")

            if not answer or len(answer.strip()) == 0:
                return AgentOutput(
                    success=True,
                    data={
                        "valid": False,
                        "confidence": 0.95,
                        "reason": "Answer is empty",
                        "issues": ["No content provided"],
                    },
                    confidence=0.95,
                )

            # Validate answer properties
            validation_prompt = f"""Evaluate this Q&A for quality:

Query: {query}
Answer: {answer}

Check:
1. Relevance: Does answer address the query?
2. Completeness: Is the answer complete?
3. Accuracy: Are there obvious errors?
4. Length: Is it substantive (not just 'yes/no')?

Return JSON:
{{
  "valid": bool,
  "relevance_score": 0-1,
  "completeness_score": 0-1,
  "accuracy_score": 0-1,
  "length_adequate": bool,
  "issues": [list of problems],
  "recommendation": "Accept/Revise/Reject"
}}"""

            response = self.llm.generate_text([
                {"role": "system", "content": "You are a quality assurance validator. Respond with valid JSON only."},
                {"role": "user", "content": validation_prompt}
            ])

            try:
                validation_result = json.loads(response)
                avg_score = (
                    validation_result.get("relevance_score", 0.5) +
                    validation_result.get("completeness_score", 0.5) +
                    validation_result.get("accuracy_score", 0.5)
                ) / 3

                is_valid = validation_result.get("valid", False) and avg_score >= 0.7

                return AgentOutput(
                    success=True,
                    data={
                        "valid": is_valid,
                        "confidence": min(avg_score, 0.99),
                        "scores": {
                            "relevance": validation_result.get("relevance_score", 0),
                            "completeness": validation_result.get("completeness_score", 0),
                            "accuracy": validation_result.get("accuracy_score", 0),
                            "average": avg_score,
                        },
                        "issues": validation_result.get("issues", []),
                        "recommendation": validation_result.get("recommendation", "Accept"),
                    },
                    confidence=min(avg_score, 0.99),
                )
            except json.JSONDecodeError:
                # Fallback to simple validation if JSON parsing fails
                is_valid = len(answer) > 20 and "error" not in answer.lower()
                confidence = 0.7 if is_valid else 0.4

                return AgentOutput(
                    success=True,
                    data={
                        "valid": is_valid,
                        "confidence": confidence,
                        "reason": "Answer validation completed",
                        "issues": [] if is_valid else ["Answer quality concerns"],
                    },
                    confidence=confidence,
                )

        except Exception as e:
            return AgentOutput(
                success=False,
                error=f"Validation failed: {str(e)[:100]}",
                confidence=0.0,
            )
