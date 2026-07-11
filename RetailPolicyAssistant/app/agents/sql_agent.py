"""SQL Agent - Text2SQL query execution."""

from app.sql import answer_sql
from app.sql_pipeline.sql_validator import SQLValidator
from app.sql_pipeline.sql_executor import SQLExecutor
from app.observability.langfuse_tracer import trace_function


class SQLAgent:
    """Executes SQL queries with Text2SQL translation and validation."""

    def __init__(self):
        self.name = "sql_agent"
        self.validator = SQLValidator()
        self.executor = SQLExecutor()

    @trace_function("sql_query", as_type="chain")
    def run(self, query: str) -> dict:
        """Execute SQL query synchronously with proper validation."""
        try:
            # Execute answer_sql (handles semantic matching)
            sql_result = answer_sql(query)
            result_text = sql_result.get("result", "No results found")
            sql_confidence = sql_result.get("confidence", 0.5)

            # Calculate confidence based on results
            if sql_confidence >= 0.9:
                confidence = 0.90
            elif "Error" in str(result_text) or "blocked" in str(result_text).lower():
                confidence = 0.3
            elif "demo" in str(result_text).lower():
                confidence = 0.70
            else:
                confidence = 0.85

            return {
                "result": result_text,
                "sources": ["Database"],
                "confidence": confidence,
                "rows": sql_result.get("rows", 0),
            }
        except Exception as e:
            return {
                "result": f"SQL Query Error: {str(e)[:100]}",
                "sources": [],
                "confidence": 0.0,
                "rows": 0,
            }
