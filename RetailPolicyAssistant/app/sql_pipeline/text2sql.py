"""Text2SQL - Converts natural language to SQL queries."""

from app.llm import LLMService


class Text2SQL:
    """Translates natural language queries to SQL."""

    def __init__(self):
        self.llm = LLMService()

    def translate_to_sql(self, query: str, schema: str = "") -> str:
        """Convert natural language query to SQL."""
        prompt = f"""Convert this to SQL:
Query: {query}
{f"Schema: {schema}" if schema else ""}
Return only SQL, no explanation."""

        sql = self.llm.generate_text([
            {"role": "system", "content": "You are a SQL expert."},
            {"role": "user", "content": prompt}
        ])
        return sql

    def generate_with_schema(self, query: str, db_schema: dict) -> str:
        """Generate SQL based on database schema."""
        schema_str = self._format_schema(db_schema)
        return self.translate_to_sql(query, schema_str)

    def _format_schema(self, schema: dict) -> str:
        """Format database schema for LLM."""
        return ""
