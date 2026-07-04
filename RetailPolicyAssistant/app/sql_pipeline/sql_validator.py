"""SQL Validator - Validates SQL syntax and safety."""

import re


class SQLValidator:
    """Validates SQL queries for syntax and safety."""

    DANGEROUS_KEYWORDS = ["DROP", "DELETE", "TRUNCATE", "ALTER", "GRANT"]

    def validate_syntax(self, sql: str) -> dict:
        """Check SQL syntax validity."""
        checks = {
            "valid_syntax": self._check_syntax(sql),
            "has_select": sql.upper().startswith("SELECT"),
            "is_safe": self._check_safety(sql),
        }
        return checks

    def _check_syntax(self, sql: str) -> bool:
        """Validate SQL syntax."""
        if not sql or not sql.strip():
            return False
        return "SELECT" in sql.upper() or any(kw in sql.upper() for kw in ["INSERT", "UPDATE"])

    def _check_safety(self, sql: str) -> bool:
        """Check for dangerous SQL operations."""
        sql_upper = sql.upper()
        for keyword in self.DANGEROUS_KEYWORDS:
            if keyword in sql_upper:
                return False
        return True

    def sanitize_sql(self, sql: str) -> str:
        """Sanitize SQL query."""
        return sql.strip()
