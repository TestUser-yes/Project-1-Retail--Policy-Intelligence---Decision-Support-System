"""SQL Agent - Text2SQL query execution."""

from app.sql import answer_sql
from app.observability.langfuse_tracer import trace_function


class SQLAgent:
    """Executes SQL queries with Text2SQL translation."""

    def __init__(self):
        self.name = "sql_agent"

    @trace_function("sql_query", as_type="chain")
    def run(self, query: str) -> dict:
        """Execute SQL query synchronously."""
        try:
            sql_result = answer_sql(query)
            # answer_sql returns dict with 'result' and 'confidence' keys
            result_text = sql_result.get("result", "No results found")
            sql_confidence = sql_result.get("confidence", 0.5)

            # Use SQL query confidence, boost if successful
            if sql_confidence >= 0.9:
                confidence = 0.90
            elif "Error" in str(result_text):
                confidence = 0.3
            else:
                confidence = 0.85

            return {
                "result": result_text,
                "sources": ["Database"],
                "confidence": confidence,
            }
        except Exception as e:
            return {
                "result": f"SQL Error: {str(e)}",
                "sources": [],
                "confidence": 0.0,
            }
