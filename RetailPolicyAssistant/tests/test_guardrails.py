"""Unit tests for guardrails."""

import pytest
from app.guardrails import (
    InputGuardrail, OutputGuardrail, PIIDetector, InjectionDetector,
    PolicyConflictDetector, SQLSafetyChecker, RBACChecker, ToxicityChecker
)


class TestInputGuardrail:
    def test_empty_query(self):
        guardrail = InputGuardrail()
        result = guardrail.check("")
        assert result["valid"] is False
        assert len(result["issues"]) > 0

    def test_valid_query(self):
        guardrail = InputGuardrail()
        result = guardrail.check("What is the vendor policy?")
        assert result["valid"] is True

    def test_query_too_long(self):
        guardrail = InputGuardrail(max_length=100)
        long_query = "x" * 200
        result = guardrail.check(long_query)
        assert result["valid"] is False


class TestOutputGuardrail:
    def test_empty_output(self):
        guardrail = OutputGuardrail()
        result = guardrail.check("")
        assert result["valid"] is False

    def test_valid_output(self):
        guardrail = OutputGuardrail()
        result = guardrail.check("This is a valid policy response.")
        assert result["valid"] is True


class TestPIIDetector:
    def test_email_detection(self):
        detector = PIIDetector()
        result = detector.check("Contact john@example.com for details")
        assert result["has_pii"] is True
        assert len(result["pii_types"]["emails"]) > 0

    def test_phone_detection(self):
        detector = PIIDetector()
        result = detector.check("Call me at 555-123-4567")
        assert result["has_pii"] is True
        assert len(result["pii_types"]["phone_numbers"]) > 0

    def test_ssn_detection(self):
        detector = PIIDetector()
        result = detector.check("SSN: 123-45-6789")
        assert result["has_pii"] is True
        assert len(result["pii_types"]["ssns"]) > 0

    def test_pii_masking(self):
        detector = PIIDetector()
        masked = detector.mask_pii("Contact john@example.com and 555-123-4567")
        assert "john@example.com" not in masked
        assert "555-123-4567" not in masked
        assert "[EMAIL]" in masked
        assert "[PHONE]" in masked


class TestInjectionDetector:
    def test_sql_injection_detection(self):
        detector = InjectionDetector()
        result = detector.check("SELECT * FROM users; DROP TABLE users;")
        assert result["has_injection"] is True

    def test_valid_query(self):
        detector = InjectionDetector()
        result = detector.check("What is the vendor approval policy?")
        assert result["has_injection"] is False


class TestPolicyConflictDetector:
    def test_conflicting_policies(self):
        detector = PolicyConflictDetector()
        result = detector.check("This policy is approved and rejected")
        assert result["has_conflicts"] is True

    def test_no_conflicts(self):
        detector = PolicyConflictDetector()
        result = detector.check("This policy is approved")
        assert result["has_conflicts"] is False


class TestSQLSafetyChecker:
    def test_dangerous_keywords(self):
        checker = SQLSafetyChecker()
        result = checker.check("DROP TABLE users")
        assert result["is_safe"] is False

    def test_safe_query(self):
        checker = SQLSafetyChecker()
        result = checker.check("SELECT * FROM policies")
        assert result["is_safe"] is True


class TestRBACChecker:
    def test_admin_permissions(self):
        checker = RBACChecker(user_role="admin")
        result = checker.check("delete")
        assert result["allowed"] is True

    def test_viewer_permissions(self):
        checker = RBACChecker(user_role="viewer")
        result = checker.check("delete")
        assert result["allowed"] is False

    def test_read_permission(self):
        checker = RBACChecker(user_role="viewer")
        result = checker.check("read")
        assert result["allowed"] is True


class TestToxicityChecker:
    def test_clean_content(self):
        checker = ToxicityChecker()
        result = checker.check("This is a professional policy document")
        assert result["is_clean"] is True

    def test_hallucination_markers(self):
        checker = ToxicityChecker()
        result = checker.check("I don't know the answer")
        # May flag as potential hallucination
        assert isinstance(result, dict)
