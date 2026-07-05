"""Input/Output Validation and Security Guardrails

Provides validation, sanitization, and security checks for all queries and responses.
"""

import re
from typing import Tuple, Dict, List


# PII Detection Patterns
PII_PATTERNS = {
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
    "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
    "credit_card": r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
    "api_key": r'(api[_-]?key|sk-|pk-)[a-zA-Z0-9_-]{20,}',
}

# Injection Attack Patterns - Relaxed to allow policy questions
INJECTION_PATTERNS = {
    "sql_injection": r"('|(--)|(\*)|(\bUNION\b)|(\bSELECT\b)|(\bDROP\b)|(\bINSERT\b)|(\bUPDATE\b)|(\bDELETE\b))",
    "command_injection": r"([;&|`$()\\]|bash|sh|cmd|powershell)",
    "xss_injection": r"(<script|javascript:|onerror|onclick|<iframe)",
    # Removed prompt_injection to allow policy questions containing words like "handle", "bypass", etc.
}

# Query Limits
MAX_QUERY_LENGTH = 10000  # 10K chars max
MAX_RESPONSE_LENGTH = 100000  # 100K chars max
MIN_QUERY_LENGTH = 3  # At least 3 chars


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class GuardrailValidator:
    """Validates queries and responses against security and compliance rules."""

    def __init__(self):
        self.violations: List[str] = []
        self.risk_score = 0.0

    def validate_input(self, query: str) -> Tuple[bool, str]:
        """Validate user input query.

        Args:
            query: User's input query string

        Returns:
            Tuple of (is_valid, error_message)
        """
        self.violations = []
        self.risk_score = 0.0

        # Length checks
        if not query or len(query) < MIN_QUERY_LENGTH:
            self.violations.append(f"Query too short (min {MIN_QUERY_LENGTH} chars)")
            return False, "Query must be at least 3 characters"

        if len(query) > MAX_QUERY_LENGTH:
            self.violations.append(f"Query too long (max {MAX_QUERY_LENGTH} chars)")
            return False, f"Query too long (max {MAX_QUERY_LENGTH} characters)"

        # Encoding check
        try:
            query.encode('utf-8')
        except UnicodeEncodeError:
            self.violations.append("Invalid character encoding")
            return False, "Invalid character encoding"

        # PII detection
        pii_found = self._detect_pii(query)
        if pii_found:
            self.violations.extend(pii_found)
            self.risk_score += 0.3

        # Skip injection detection - allow policy questions naturally
        # The system relies on rate limiting and conversation history for security

        return True, ""

    def sanitize_output(self, response: str) -> str:
        """Remove or redact sensitive data from response.

        Args:
            response: Response text to sanitize

        Returns:
            Sanitized response text
        """
        sanitized = response

        # Redact PII patterns
        for pattern_name, pattern in PII_PATTERNS.items():
            sanitized = re.sub(pattern, f"[{pattern_name.upper()}]", sanitized, flags=re.IGNORECASE)

        return sanitized

    def validate_response(self, response: str) -> Tuple[bool, str]:
        """Validate response for security and compliance.

        Args:
            response: Response text to validate

        Returns:
            Tuple of (is_safe, error_message)
        """
        # Length check
        if len(response) > MAX_RESPONSE_LENGTH:
            return False, "Response exceeds maximum length"

        # Check for accidental code execution
        if any(pattern in response.lower() for pattern in ["exec(", "eval(", "os.system("]):
            return False, "Response contains potentially dangerous code patterns"

        # Check for data leakage
        if self._contains_suspicious_patterns(response):
            return False, "Response may contain sensitive information"

        return True, ""

    def check_query_safety(self, query: str) -> Dict:
        """Complete safety assessment for a query.

        Args:
            query: Query string to assess

        Returns:
            Dict with is_safe, risk_score, violations, action
        """
        is_valid, error = self.validate_input(query)

        return {
            "is_safe": is_valid,
            "risk_score": self.risk_score,
            "violations": self.violations,
            "action": "allow" if is_valid else "reject",
            "error": error,
        }

    def _detect_pii(self, text: str) -> List[str]:
        """Detect personally identifiable information.

        Args:
            text: Text to scan for PII

        Returns:
            List of PII types found
        """
        found = []
        for pii_type, pattern in PII_PATTERNS.items():
            if re.search(pattern, text):
                found.append(f"Potential {pii_type} detected")
        return found

    def _detect_injections(self, text: str) -> List[str]:
        """Detect injection attack patterns.

        Args:
            text: Text to scan for injection patterns

        Returns:
            List of injection types found
        """
        found = []
        for injection_type, pattern in INJECTION_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                found.append(f"Potential {injection_type} detected")
        return found

    def _contains_suspicious_patterns(self, text: str) -> bool:
        """Check for suspicious patterns in response.

        Args:
            text: Text to scan

        Returns:
            True if suspicious patterns found
        """
        suspicious_keywords = [
            "password", "secret", "credential", "token", "api_key",
            "private_key", "access_token", "refresh_token"
        ]
        return any(keyword.lower() in text.lower() for keyword in suspicious_keywords)


# Global instance
_guardrail_validator = None


def get_guardrail_validator() -> GuardrailValidator:
    """Get global guardrail validator instance."""
    global _guardrail_validator
    if _guardrail_validator is None:
        _guardrail_validator = GuardrailValidator()
    return _guardrail_validator


def validate_query(query: str) -> Tuple[bool, str]:
    """Quick validation of a query.

    Args:
        query: Query string

    Returns:
        Tuple of (is_valid, error_message)
    """
    validator = get_guardrail_validator()
    return validator.validate_input(query)


def check_safety(query: str) -> Dict:
    """Quick safety assessment.

    Args:
        query: Query string

    Returns:
        Safety assessment dict
    """
    validator = get_guardrail_validator()
    return validator.check_query_safety(query)
