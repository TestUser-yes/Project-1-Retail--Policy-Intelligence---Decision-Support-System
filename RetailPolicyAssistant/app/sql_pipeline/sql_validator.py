"""SQL Validator - Validates SQL syntax and safety."""

import re
from typing import Dict, Tuple


class SQLValidator:
    """Validates SQL queries for syntax and safety."""

    DANGEROUS_KEYWORDS = ["DROP", "DELETE", "TRUNCATE", "ALTER", "GRANT", "REVOKE", "CREATE", "REPLACE"]
    INJECTION_PATTERNS = [
        r";\s*(DROP|DELETE|TRUNCATE|ALTER|INSERT|UPDATE|CREATE)",  # Multiple statements
        r"--\s",  # SQL comments
        r"/\*.*?\*/",  # Block comments
        r"'\s*(OR|AND)\s*'.*?=",  # Basic OR injection
        r"xp_",  # Extended stored procedures
        r"sp_",  # System stored procedures (suspicious usage)
    ]

    def validate_syntax(self, sql: str) -> Dict:
        """Check SQL syntax validity."""
        if not sql or not sql.strip():
            return {
                "valid": False,
                "reason": "Empty SQL query",
            }

        checks = {
            "valid_syntax": self._check_syntax(sql),
            "has_select": sql.upper().startswith("SELECT"),
            "is_safe": self._check_safety(sql),
            "safe": self._check_syntax(sql) and self._check_safety(sql),
        }
        return checks

    def _check_syntax(self, sql: str) -> bool:
        """Validate SQL syntax."""
        if not sql or not sql.strip():
            return False

        sql_upper = sql.upper().strip()

        # Only allow SELECT, INSERT (with VALUES), UPDATE (with WHERE), or read-only operations
        allowed_starts = ["SELECT", "WITH"]
        is_allowed = any(sql_upper.startswith(start) for start in allowed_starts)

        if not is_allowed:
            return False

        # Ensure balanced parentheses
        if sql.count("(") != sql.count(")"):
            return False

        # Check for basic structure
        return True

    def _check_safety(self, sql: str) -> bool:
        """Check for dangerous SQL operations and injection patterns."""
        sql_upper = sql.upper()

        # Block dangerous keywords
        for keyword in self.DANGEROUS_KEYWORDS:
            if f" {keyword} " in f" {sql_upper} ":  # Word boundary check
                return False

        # Check for injection patterns
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, sql, re.IGNORECASE):
                return False

        return True

    def sanitize_sql(self, sql: str) -> str:
        """Sanitize SQL query."""
        sql = sql.strip()

        # Remove leading/trailing whitespace and newlines
        sql = "\n".join(line.strip() for line in sql.split("\n") if line.strip())

        return sql

    def validate_and_sanitize(self, sql: str) -> Tuple[bool, str, str]:
        """Validate and sanitize SQL, returning (is_valid, sanitized_sql, error_message)."""
        if not sql or not sql.strip():
            return False, "", "Empty SQL query"

        sanitized = self.sanitize_sql(sql)
        validation = self.validate_syntax(sanitized)

        if not validation.get("safe", False):
            reason = "Query contains unsafe patterns or dangerous keywords"
            return False, sanitized, reason

        return True, sanitized, ""
