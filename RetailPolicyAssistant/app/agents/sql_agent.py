"""SQL Agent - Text2SQL query execution."""

from app.agents.base_agent import BaseAgent, AgentInput, AgentOutput
from app.sql import answer_sql


class SQLAgent(BaseAgent):
    """Executes SQL queries with Text2SQL translation."""

    def __init__(self):
        super().__init__(name="sql_agent", description="SQL executor")

    async def _execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute SQL query."""
        query = agent_input.query

        try:
            result = answer_sql(query)
            confidence = 0.85 if result else 0.5

            return AgentOutput(
                success=True,
                data={"result": result},
                confidence=confidence,
            )
        except Exception as e:
            return AgentOutput(
                success=False,
                error=str(e),
                confidence=0.0,
            )
