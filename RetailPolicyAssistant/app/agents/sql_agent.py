"""SQL Agent - Text2SQL query execution."""

from app.sql import answer_sql


class SQLAgent:
    """Executes SQL queries with Text2SQL translation."""

    def __init__(self):
        self.name = "sql_agent"

    def run(self, query: str) -> dict:
        """Execute SQL query synchronously."""
        try:
            result = answer_sql(query)
            confidence = 0.88 if result and "Error" not in str(result) else 0.3

            return {
                "result": result,
                "sources": ["Database"],
                "confidence": confidence,
            }
        except Exception as e:
            return {
                "result": f"SQL Error: {str(e)}",
                "sources": [],
                "confidence": 0.0,
            }
