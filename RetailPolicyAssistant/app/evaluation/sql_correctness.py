"""SQL Correctness evaluation - validates SQL query quality and safety."""

from dataclasses import dataclass
from typing import Optional, List, Tuple
import re


@dataclass
class SQLCorrectnessResult:
    """Result of SQL correctness evaluation."""

    is_correct: bool  # Overall correctness
    confidence: float  # 0.0-1.0
    syntax_valid: bool  # SQL syntax is valid
    injection_safe: bool  # No SQL injection detected
    execution_successful: bool  # Query executed without error
    result_valid: bool  # Result set is valid

    issues: List[str] = None  # List of issues found
    warnings: List[str] = None  # Non-critical warnings

    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.warnings is None:
            self.warnings = []

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "is_correct": self.is_correct,
            "confidence": round(self.confidence, 3),
            "syntax_valid": self.syntax_valid,
            "injection_safe": self.injection_safe,
            "execution_successful": self.execution_successful,
            "result_valid": self.result_valid,
            "issues": self.issues,
            "warnings": self.warnings,
        }


class SQLValidator:
    """Validates SQL queries for correctness and safety."""

    # SQL Injection patterns to detect
    SQL_INJECTION_PATTERNS = [
        r"(--|#|/\*)",  # SQL comments
        r"(\bor\b.*=.*)",  # or logic
        r"(\band\b.*=.*)",  # and logic with suspicious patterns
        r"(union.*select)",  # UNION-based injection
        r"(;.*drop)",  # DROP statements
        r"(;.*delete)",  # DELETE statements
        r"(;.*truncate)",  # TRUNCATE statements
        r"(exec\s*\()",  # Dynamic SQL execution
        r"(execute\s*\()",  # Dynamic SQL execution
        r"(\beval\b)",  # eval() calls
        r"(\bxp_)",  # Extended stored procedures
    ]

    # Keywords that indicate valid SQL
    VALID_SQL_KEYWORDS = {
        "select", "from", "where", "join", "left", "right", "inner",
        "group", "by", "order", "limit", "offset", "having",
        "distinct", "count", "sum", "avg", "min", "max",
    }

    # Keywords that are dangerous (should not appear in most queries)
    DANGEROUS_KEYWORDS = {
        "drop", "delete", "truncate", "alter", "create", "exec",
        "execute", "xp_", "sp_", "script", "javascript", "xml",
    }

    def __init__(self):
        """Initialize SQL validator."""
        self.compiled_injection_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.SQL_INJECTION_PATTERNS
        ]

    def validate_syntax(self, query: str) -> Tuple[bool, List[str]]:
        """Validate SQL query syntax.

        Args:
            query: SQL query string

        Returns:
            (is_valid, issues) tuple
        """
        issues = []

        if not query or not query.strip():
            issues.append("Query is empty")
            return False, issues

        query_lower = query.lower().strip()

        # Check for common syntax errors
        if query_lower.count("(") != query_lower.count(")"):
            issues.append("Mismatched parentheses")

        if query_lower.count("'") % 2 != 0:
            issues.append("Mismatched quotes")

        # Check for at least one valid SQL keyword
        has_valid_keyword = any(keyword in query_lower for keyword in self.VALID_SQL_KEYWORDS)
        if not has_valid_keyword:
            issues.append("No valid SQL keywords found")
            return False, issues

        # Basic syntax check - must start with SELECT (for read queries)
        if not query_lower.startswith("select"):
            if not any(query_lower.startswith(kw) for kw in ["select", "with"]):
                issues.append("Query does not start with SELECT or WITH")
                return False, issues

        return len(issues) == 0, issues

    def check_sql_injection(self, query: str) -> Tuple[bool, List[str]]:
        """Check for SQL injection patterns.

        Args:
            query: SQL query string

        Returns:
            (is_safe, issues) tuple
        """
        issues = []

        query_lower = query.lower()

        # Check compiled patterns
        for pattern in self.compiled_injection_patterns:
            if pattern.search(query_lower):
                issues.append(f"Potential injection pattern detected: {pattern.pattern}")

        # Check for dangerous keywords
        for keyword in self.DANGEROUS_KEYWORDS:
            if f" {keyword} " in f" {query_lower} " or query_lower.startswith(keyword):
                issues.append(f"Dangerous keyword found: {keyword}")

        return len(issues) == 0, issues

    def validate_execution(
        self,
        query: str,
        execution_succeeded: bool,
        execution_error: Optional[str] = None,
        row_count: Optional[int] = None,
    ) -> Tuple[bool, List[str]]:
        """Validate query execution results.

        Args:
            query: SQL query string
            execution_succeeded: Whether execution was successful
            execution_error: Error message if execution failed
            row_count: Number of rows returned

        Returns:
            (is_valid, issues) tuple
        """
        issues = []
        warnings = []

        if not execution_succeeded:
            issues.append(f"Execution failed: {execution_error or 'Unknown error'}")
            return False, issues

        # Check for reasonable result sizes
        if row_count is not None:
            if row_count == 0 and "count(" not in query.lower():
                warnings.append("Query returned no results")
            elif row_count > 10000:
                warnings.append(f"Query returned large result set ({row_count} rows)")

        return True, issues

    def evaluate_query(
        self,
        query: str,
        execution_succeeded: bool = True,
        execution_error: Optional[str] = None,
        row_count: Optional[int] = None,
    ) -> SQLCorrectnessResult:
        """Comprehensively evaluate SQL query correctness.

        Args:
            query: SQL query string
            execution_succeeded: Whether query executed successfully
            execution_error: Error message if execution failed
            row_count: Number of rows returned

        Returns:
            SQLCorrectnessResult with detailed validation info
        """
        all_issues = []
        all_warnings = []

        # 1. Syntax validation
        syntax_valid, syntax_issues = self.validate_syntax(query)
        all_issues.extend(syntax_issues)

        # 2. Injection detection
        injection_safe, injection_issues = self.check_sql_injection(query)
        all_issues.extend(injection_issues)

        # 3. Execution validation
        exec_valid, exec_issues = self.validate_execution(
            query, execution_succeeded, execution_error, row_count
        )
        all_issues.extend(exec_issues)

        # 4. Result validation
        result_valid = exec_valid and syntax_valid

        # Calculate overall correctness and confidence
        is_correct = syntax_valid and injection_safe and exec_valid and result_valid

        # Confidence based on individual checks
        confidence_score = 0.0
        if syntax_valid:
            confidence_score += 0.25
        if injection_safe:
            confidence_score += 0.25
        if exec_valid:
            confidence_score += 0.25
        if result_valid:
            confidence_score += 0.25

        return SQLCorrectnessResult(
            is_correct=is_correct,
            confidence=confidence_score,
            syntax_valid=syntax_valid,
            injection_safe=injection_safe,
            execution_successful=execution_succeeded,
            result_valid=result_valid,
            issues=all_issues,
            warnings=all_warnings,
        )


# Global validator instance
_sql_validator: Optional[SQLValidator] = None


def get_sql_validator() -> SQLValidator:
    """Get global SQL validator instance."""
    global _sql_validator
    if _sql_validator is None:
        _sql_validator = SQLValidator()
    return _sql_validator


def validate_sql(
    query: str,
    execution_succeeded: bool = True,
    execution_error: Optional[str] = None,
    row_count: Optional[int] = None,
) -> SQLCorrectnessResult:
    """Validate a SQL query and return correctness score.

    Args:
        query: SQL query string
        execution_succeeded: Whether execution succeeded
        execution_error: Error message if execution failed
        row_count: Number of result rows

    Returns:
        SQLCorrectnessResult
    """
    validator = get_sql_validator()
    return validator.evaluate_query(query, execution_succeeded, execution_error, row_count)


class SQLCorrectnessTracker:
    """Track SQL correctness metrics over time."""

    def __init__(self):
        self.evaluations: List[SQLCorrectnessResult] = []

    def record_evaluation(self, result: SQLCorrectnessResult) -> None:
        """Record a SQL evaluation result."""
        self.evaluations.append(result)

    def get_summary(self) -> dict:
        """Get summary of SQL correctness metrics.

        Returns:
            {
                "total_queries": int,
                "correct_queries": int,
                "correctness_rate": float,
                "syntax_pass_rate": float,
                "injection_safe_rate": float,
                "execution_success_rate": float,
                "average_confidence": float,
            }
        """
        if not self.evaluations:
            return {
                "total_queries": 0,
                "correct_queries": 0,
                "correctness_rate": 0.0,
                "average_confidence": 0.0,
            }

        total = len(self.evaluations)
        correct = sum(1 for e in self.evaluations if e.is_correct)
        syntax_valid = sum(1 for e in self.evaluations if e.syntax_valid)
        injection_safe = sum(1 for e in self.evaluations if e.injection_safe)
        exec_success = sum(1 for e in self.evaluations if e.execution_successful)
        avg_confidence = sum(e.confidence for e in self.evaluations) / total

        return {
            "total_queries": total,
            "correct_queries": correct,
            "correctness_rate": round(correct / total, 4) if total > 0 else 0.0,
            "syntax_pass_rate": round(syntax_valid / total, 4) if total > 0 else 0.0,
            "injection_safe_rate": round(injection_safe / total, 4) if total > 0 else 0.0,
            "execution_success_rate": round(exec_success / total, 4) if total > 0 else 0.0,
            "average_confidence": round(avg_confidence, 4),
        }
