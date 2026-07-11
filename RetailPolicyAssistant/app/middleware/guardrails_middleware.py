"""Guardrails Middleware - Central security enforcement for all queries."""

from app.guardrails import (
    InputGuardrail,
    OutputGuardrail,
    PIIDetector,
    InjectionDetector,
    PolicyConflictDetector,
    SQLSafetyChecker,
    RBACChecker,
    ToxicityChecker,
)


class GuardrailsMiddleware:
    """Centralized guardrails enforcement - all 8 layers active."""

    def __init__(self, user_role: str = "viewer"):
        self.input_guardrail = InputGuardrail(max_length=5000)
        self.output_guardrail = OutputGuardrail(min_length=10)
        self.pii_detector = PIIDetector()
        self.injection_detector = InjectionDetector()
        self.policy_conflict = PolicyConflictDetector()
        self.sql_checker = SQLSafetyChecker()
        self.rbac_checker = RBACChecker(user_role=user_role)
        self.toxicity_checker = ToxicityChecker()
        self.violations = []
        self.user_role = user_role

    def validate_input(self, query: str) -> tuple:
        """Run all input validation layers (1-5).

        Returns:
            (is_valid: bool, violations: list)
        """
        self.violations = []

        # Layer 1: Input validation
        input_check = self.input_guardrail.check(query)
        if not input_check["valid"]:
            self.violations.extend(input_check["issues"])
            return False, self.violations

        # Layer 3: PII detection (warning only, don't block)
        pii_check = self.pii_detector.check(query)
        if pii_check["has_pii"]:
            self.violations.append(f"Warning: PII detected in query: {pii_check['pii_types']}")

        # Layer 4: Injection detection (block)
        injection_check = self.injection_detector.check(query)
        if injection_check["has_injection"]:
            self.violations.extend(injection_check["injections"])
            return False, self.violations

        # Layer 5: Policy conflict detection (block)
        conflict_check = self.policy_conflict.check(query)
        if conflict_check["has_conflicts"]:
            self.violations.extend(conflict_check["conflicts"])
            return False, self.violations

        # Layer 6: SQL safety check (block if destructive)
        if "select" in query.lower() or "from" in query.lower() or "where" in query.lower():
            sql_check = self.sql_checker.check(query)
            if not sql_check["is_safe"]:
                self.violations.append(f"Unsafe SQL keywords detected: {sql_check['unsafe_keywords']}")
                return False, self.violations

        return len([v for v in self.violations if "Warning" not in v]) == 0, self.violations

    def check_access(self, action: str) -> tuple:
        """Layer 7: Check RBAC permissions.

        Returns:
            (is_allowed: bool, reason: str)
        """
        rbac_check = self.rbac_checker.check(action)
        if rbac_check["allowed"]:
            return True, f"Access granted for action '{action}'"
        else:
            return False, f"Access denied: {self.rbac_checker.user_role} cannot {action}"

    def sanitize_output(self, response: str) -> str:
        """Run all output sanitization layers (2, 3, 8).

        - Validates output quality (Layer 2)
        - Masks PII (Layer 3)
        - Checks for toxicity/hallucinations (Layer 8)

        Returns:
            Sanitized response
        """
        # Layer 2: Output validation
        output_check = self.output_guardrail.check(response)
        if not output_check["valid"]:
            return f"[ERROR] Response failed quality check: {output_check['issues']}"

        # Layer 3: Mask PII
        response = self.pii_detector.mask_pii(response)

        # Layer 8: Toxicity/hallucination check
        tox_check = self.toxicity_checker.check(response)
        if not tox_check["is_clean"]:
            response = f"[SYSTEM WARNING: {tox_check['issues']}]\n{response}"

        return response

    def get_summary(self) -> dict:
        """Get summary of all checks."""
        return {
            "violations": self.violations,
            "user_role": self.rbac_checker.user_role,
            "is_safe": len([v for v in self.violations if "Warning" not in v]) == 0,
        }


# Global instance
_middleware = None


def get_guardrails_middleware(user_role: str = "viewer") -> GuardrailsMiddleware:
    """Get or create guardrails middleware instance."""
    global _middleware
    if _middleware is None:
        _middleware = GuardrailsMiddleware(user_role=user_role)
    else:
        _middleware.user_role = user_role
        _middleware.rbac_checker.user_role = user_role
    return _middleware
