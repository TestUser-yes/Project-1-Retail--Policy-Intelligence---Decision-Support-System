"""SQL Safety Checker - Layer 6: Validates SQL safety."""


class SQLSafetyChecker:
    """Checks SQL query safety."""

    UNSAFE_KEYWORDS = ["DROP", "DELETE", "TRUNCATE", "ALTER", "GRANT", "REVOKE"]

    def check(self, sql: str) -> dict:
        """Check SQL safety."""
        sql_upper = sql.upper()
        unsafe_keywords = []

        for keyword in self.UNSAFE_KEYWORDS:
            if keyword in sql_upper:
                unsafe_keywords.append(keyword)

        return {
            "is_safe": len(unsafe_keywords) == 0,
            "unsafe_keywords": unsafe_keywords,
        }
