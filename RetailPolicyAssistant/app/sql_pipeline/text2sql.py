"""Text2SQL - Converts natural language to SQL queries."""

from typing import Dict, List
from app.llm import LLMService


class Text2SQL:
    """Translates natural language queries to SQL."""

    def __init__(self):
        self.llm = LLMService()

    def translate_to_sql(self, query: str, schema: str = "") -> str:
        """Convert natural language query to SQL."""
        prompt = f"""You are a SQL expert. Convert the user's natural language query into valid SQL.

{f'Schema Information:{chr(10)}{schema}{chr(10)}' if schema else ''}
Instructions:
1. Generate ONLY valid SQL, no explanation
2. Use SELECT statements for queries
3. Ensure proper syntax with correct table and column names
4. Return a single SQL statement

User Query: {query}

Return only the SQL statement:"""

        sql = self.llm.generate_text([
            {"role": "system", "content": "You are a SQL expert. Generate only valid, safe SQL queries."},
            {"role": "user", "content": prompt}
        ])
        return sql.strip()

    def generate_with_schema(self, query: str, db_schema: Dict) -> str:
        """Generate SQL based on database schema."""
        schema_str = self._format_schema(db_schema)
        return self.translate_to_sql(query, schema_str)

    def _format_schema(self, schema: Dict) -> str:
        """Format database schema for LLM."""
        if not schema:
            return ""

        formatted_lines = []
        for table_name, table_info in schema.items():
            columns = table_info.get("columns", [])
            primary_key = table_info.get("primary_key", "")

            col_str = ", ".join(
                f"{col['name']} ({col['type']})"
                for col in columns
            )

            formatted_lines.append(f"Table: {table_name}")
            formatted_lines.append(f"  Columns: {col_str}")
            if primary_key:
                formatted_lines.append(f"  Primary Key: {primary_key}")

        return "\n".join(formatted_lines)
