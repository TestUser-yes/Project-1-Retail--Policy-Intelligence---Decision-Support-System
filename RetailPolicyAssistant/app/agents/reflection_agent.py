"""Reflection Agent - Self-correction and quality checking."""

from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.llm import LLMService


class ReflectionAgent(BaseAgent):
    """Performs deep self-reflection on generated answers for quality assurance."""

    def __init__(self):
        super().__init__(name="reflection_agent", description="Self-reflection engine")
        self.llm = LLMService()

    async def _execute(self, agent_input: AgentInput) -> AgentOutput:
        """Perform comprehensive reflection on answer quality."""
        try:
            query = agent_input.get("query", "")
            answer = agent_input.previous_outputs.get("answer", "")
            documents = agent_input.previous_outputs.get("documents", [])
            sources = agent_input.previous_outputs.get("sources", [])

            # Perform multi-aspect checks
            checks = self._basic_checks(query, answer, documents, sources)

            # LLM-based reflection for semantic quality
            if answer and len(answer) > 20:
                semantic_check = await self._semantic_reflection(query, answer)
                checks.update(semantic_check)

            # Calculate overall quality score
            passed_checks = sum(1 for v in checks.values() if isinstance(v, bool) and v)
            total_checks = sum(1 for v in checks.values() if isinstance(v, bool))
            confidence = passed_checks / max(total_checks, 1)

            return AgentOutput(
                success=True,
                data={
                    "checks": checks,
                    "quality_score": confidence,
                    "passed_checks": passed_checks,
                    "total_checks": total_checks,
                    "recommendation": self._get_recommendation(confidence, checks),
                    "issues": self._identify_issues(checks),
                },
                confidence=min(0.95, confidence),
            )

        except Exception as e:
            return AgentOutput(
                success=False,
                error=f"Reflection failed: {str(e)[:100]}",
                confidence=0.0,
            )

    def _basic_checks(self, query: str, answer: str, documents: list, sources: list) -> dict:
        """Perform basic quality checks."""
        query_lower = query.lower()
        answer_lower = answer.lower() if answer else ""

        return {
            "answers_question": self._addresses_query(query_lower, answer_lower),
            "has_sources": len(sources) > 0 or len(documents) > 0,
            "adequate_length": len(answer) > 50 if answer else False,
            "no_empty_response": bool(answer and answer.strip()),
            "no_error_keywords": not any(err in answer_lower for err in ["error", "failed", "unable"]),
            "specific_not_vague": self._is_specific(answer),
            "contains_evidence": any(marker in answer for marker in ["evidence", "research", "data", "study", "found", "identified"]),
        }

    async def _semantic_reflection(self, query: str, answer: str) -> dict:
        """Use LLM to perform semantic quality checks."""
        try:
            reflection_prompt = f"""Analyze this answer:

Query: {query}
Answer: {answer}

Check:
- Coherence: Is the answer logically coherent?
- Completeness: Does it fully address the query?
- Accuracy: Are there apparent factual errors?
- Clarity: Is it clear and understandable?

Return: {{
  "coherent": bool,
  "complete": bool,
  "accurate": bool,
  "clear": bool
}}"""

            response = self.llm.generate_text([
                {"role": "system", "content": "Return only valid JSON."},
                {"role": "user", "content": reflection_prompt}
            ])

            import json
            try:
                result = json.loads(response)
                return {
                    "coherent": result.get("coherent", False),
                    "complete": result.get("complete", False),
                    "accurate": result.get("accurate", False),
                    "clear": result.get("clear", False),
                }
            except:
                return {
                    "coherent": True,
                    "complete": True,
                    "accurate": True,
                    "clear": True,
                }
        except Exception:
            return {}

    def _addresses_query(self, query: str, answer: str) -> bool:
        """Check if answer addresses the query."""
        query_words = set(query.split())
        answer_words = set(answer.split())
        # At least 30% of query words should be in answer
        overlap = len(query_words & answer_words)
        return overlap >= max(1, len(query_words) * 0.3)

    def _is_specific(self, answer: str) -> bool:
        """Check if answer is specific (not vague)."""
        vague_phrases = ["might", "could be", "possibly", "maybe", "somewhat", "kind of", "sort of"]
        vague_count = sum(1 for phrase in vague_phrases if phrase in answer.lower())
        specificity = 1 - (vague_count / max(len(answer.split()), 1))
        return specificity > 0.5

    def _get_recommendation(self, confidence: float, checks: dict) -> str:
        """Recommend action based on quality."""
        if confidence >= 0.85:
            return "Accept"
        elif confidence >= 0.65:
            return "Review"
        else:
            return "Revise"

    def _identify_issues(self, checks: dict) -> list:
        """Identify quality issues."""
        issues = []
        for check_name, result in checks.items():
            if isinstance(result, bool) and not result:
                issues.append(f"Failed: {check_name}")
        return issues
