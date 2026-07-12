"""Response Enforcer - Output validation and unsafe content blocking.

Enforces that responses don't contain code execution patterns, leaked credentials,
system prompts, or other unsafe content. Automatically sanitizes or blocks unsafe
responses.

Safety checks:
1. Code execution detection: exec(), eval(), os.system(), subprocess
2. Credential leakage: API keys, tokens, passwords
3. System prompt leakage: "system prompt", "instructions", "hidden"
4. Shell redirects: >&, |, &&
5. Function/variable exposure: function names, internal APIs
"""

import re
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger("response_enforcer")


class ResponseEnforcer:
    """Enforces safe responses by detecting and blocking/sanitizing unsafe content."""

    # Code execution patterns
    CODE_EXECUTION_PATTERNS = [
        r"\bexec\s*\(",
        r"\beval\s*\(",
        r"\bcompile\s*\(",
        r"__import__\s*\(",
        r"\beval\s*\(",
        r"\bos\.system\s*\(",
        r"\bsubprocess\.",
        r"\bsh\.run\s*\(",
        r"\bshell=True",
        r"\bbash\s*-c",
    ]

    # Credential leakage patterns
    CREDENTIAL_PATTERNS = {
        "api_key_openai": r"sk-[a-zA-Z0-9]{20,}",
        "api_key_generic": r"(?:api[_-]?key|password|secret|token)[\s]*[=:]\s*['\"]?([a-zA-Z0-9_-]{10,})['\"]?",
        "aws_key": r"AKIA[0-9A-Z]{16}",
        "jwt_token": r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
        "bearer_token": r"Bearer\s+[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",
        "database_url": r"(postgresql|mongodb|mysql|redis)://[^\s]+",
        "connection_string": r"(Server|Data Source|Host|Database)[\s]*=[\s]*[^\s;,]+",
        "password_literal": r"(?:password|passwd|pwd)[\s]*[=:]\s*['\"]?([a-zA-Z0-9!@#$%^&*()_+-=]{6,})['\"]?",
        "private_key": r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----",
    }

    # System prompt leakage patterns
    PROMPT_LEAKAGE_PATTERNS = [
        r"system\s+prompt",
        r"system\s+instruction",
        r"hidden\s+instruction",
        r"secret\s+instruction",
        r"initial\s+instruction",
        r"my\s+role\s+is",
        r"i\s+was\s+instructed",
        r"ignore\s+previous",
        r"forget\s+previous",
        r"the\s+actual\s+rule",
        r"the\s+true\s+rule",
        r"behind\s+the\s+scenes",
        r"under\s+the\s+hood",
    ]

    # Shell redirection patterns
    SHELL_REDIRECT_PATTERNS = [
        r">&\s*[0-9]",  # Output redirection: >&2, >&1
        r"[0-9]>\s*&",
        r"2>&1",
        r"\|\s*tee",  # Pipe to tee
        r">\s+/dev/",  # Output to device
    ]

    # Function/method exposure patterns (indicate code leakage)
    EXPOSED_FUNCTION_PATTERNS = [
        r"def\s+\w+\s*\(",
        r"async\s+def\s+\w+\s*\(",
        r"class\s+\w+[\s\(:]",
        r"@\w+\s*\(\s*\)",  # Decorators
        r"import\s+\w+",
        r"from\s+\w+\s+import",
    ]

    def __init__(self, block_unsafe: bool = True, sanitize: bool = True):
        """Initialize response enforcer.

        Args:
            block_unsafe: If True, block unsafe responses entirely
            sanitize: If True, attempt to sanitize instead of blocking
        """
        self.block_unsafe = block_unsafe
        self.sanitize = sanitize

    def check_response(self, response: str) -> Dict:
        """Check if response is safe.

        Args:
            response: Response text to check

        Returns:
            {
                "is_safe": bool,
                "unsafe_patterns": list[str],
                "risk_level": "none" | "low" | "medium" | "high",
                "recommended_action": "allow" | "sanitize" | "block",
                "explanation": str,
            }
        """
        unsafe_patterns = []
        risk_level = "none"

        # Check all unsafe patterns
        code_exec = self._check_code_execution(response)
        if code_exec:
            unsafe_patterns.extend(code_exec)
            risk_level = "high"

        creds = self._check_credential_leakage(response)
        if creds:
            unsafe_patterns.extend(creds)
            if risk_level != "high":
                risk_level = "high"

        prompts = self._check_prompt_leakage(response)
        if prompts:
            unsafe_patterns.extend(prompts)
            if risk_level in ["none", "low"]:
                risk_level = "medium"

        shell = self._check_shell_redirects(response)
        if shell:
            unsafe_patterns.extend(shell)
            if risk_level == "none":
                risk_level = "medium"

        functions = self._check_exposed_functions(response)
        if functions:
            unsafe_patterns.extend(functions)
            if risk_level == "none":
                risk_level = "low"

        # Determine action
        is_safe = len(unsafe_patterns) == 0
        if is_safe:
            recommended_action = "allow"
        elif self.sanitize:
            recommended_action = "sanitize"
        else:
            recommended_action = "block"

        return {
            "is_safe": is_safe,
            "unsafe_patterns": unsafe_patterns,
            "risk_level": risk_level,
            "recommended_action": recommended_action,
            "explanation": self._get_explanation(unsafe_patterns, risk_level),
        }

    def enforce(self, response: str) -> Tuple[bool, str, str]:
        """Enforce safety on response - block or sanitize.

        Args:
            response: Response text to enforce

        Returns:
            (is_safe: bool, enforced_response: str, enforcement_reason: str)
        """
        check = self.check_response(response)

        if check["is_safe"]:
            return True, response, "Response is safe"

        if check["recommended_action"] == "sanitize":
            sanitized, reason = self._sanitize_response(response)
            # Re-check sanitized response
            re_check = self.check_response(sanitized)
            if re_check["is_safe"]:
                return True, sanitized, f"Response sanitized: {reason}"
            else:
                # Sanitization failed, fall through to blocking
                if self.block_unsafe:
                    return (
                        False,
                        self._get_safe_fallback(),
                        f"Response blocked - unsafe patterns persist after sanitization: {', '.join(re_check['unsafe_patterns'])}",
                    )
                else:
                    return True, response, "Safety enforcement disabled (dev mode)"

        if self.block_unsafe:
            return (
                False,
                self._get_safe_fallback(),
                f"Response blocked - unsafe patterns detected: {', '.join(check['unsafe_patterns'])}",
            )
        else:
            return (
                True,
                response,
                "Safety enforcement disabled (dev mode)",
            )

    def _check_code_execution(self, text: str) -> list:
        """Check for code execution patterns."""
        matches = []
        for pattern in self.CODE_EXECUTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                matches.append("Code execution pattern detected")
                break  # Only report once
        return matches

    def _check_credential_leakage(self, text: str) -> list:
        """Check for credential leakage patterns."""
        matches = []
        for cred_type, pattern in self.CREDENTIAL_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                matches.append(f"Potential {cred_type} detected")
        return matches

    def _check_prompt_leakage(self, text: str) -> list:
        """Check for system prompt/instruction leakage."""
        matches = []
        for pattern in self.PROMPT_LEAKAGE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                matches.append("System prompt leakage detected")
                break  # Only report once
        return matches

    def _check_shell_redirects(self, text: str) -> list:
        """Check for shell redirection patterns."""
        matches = []
        for pattern in self.SHELL_REDIRECT_PATTERNS:
            if re.search(pattern, text):
                matches.append("Shell redirection pattern detected")
                break  # Only report once
        return matches

    def _check_exposed_functions(self, text: str) -> list:
        """Check for exposed function/method definitions."""
        matches = []
        for pattern in self.EXPOSED_FUNCTION_PATTERNS:
            if re.search(pattern, text):
                matches.append("Code structure exposure detected")
                break  # Only report once
        return matches

    def _sanitize_response(self, response: str) -> Tuple[str, str]:
        """Sanitize unsafe content from response.

        Args:
            response: Unsafe response text

        Returns:
            (sanitized_response: str, reason: str)
        """
        sanitized = response
        reasons = []

        # Remove code execution patterns
        for pattern in self.CODE_EXECUTION_PATTERNS:
            if re.search(pattern, sanitized, re.IGNORECASE):
                sanitized = re.sub(
                    pattern,
                    "[CODE_REMOVED]",
                    sanitized,
                    flags=re.IGNORECASE,
                )
                reasons.append("Removed code execution patterns")
                break

        # Mask credentials
        for cred_type, pattern in self.CREDENTIAL_PATTERNS.items():
            if re.search(pattern, sanitized, re.IGNORECASE):
                sanitized = re.sub(
                    pattern,
                    f"[{cred_type.upper().replace('_', '_')}]",
                    sanitized,
                    flags=re.IGNORECASE,
                )
                reasons.append(f"Masked {cred_type}")

        # Remove prompt leakage references
        for pattern in self.PROMPT_LEAKAGE_PATTERNS:
            if re.search(pattern, sanitized, re.IGNORECASE):
                sanitized = re.sub(
                    pattern,
                    "[SYSTEM_REFERENCE_REMOVED]",
                    sanitized,
                    flags=re.IGNORECASE,
                )
                reasons.append("Removed system prompt references")
                break

        # Remove shell redirects
        for pattern in self.SHELL_REDIRECT_PATTERNS:
            if re.search(pattern, sanitized):
                sanitized = re.sub(pattern, "[SHELL_REDIRECT_REMOVED]", sanitized)
                reasons.append("Removed shell redirects")
                break

        # Remove code structure exposures
        for pattern in self.EXPOSED_FUNCTION_PATTERNS:
            if re.search(pattern, sanitized):
                sanitized = re.sub(
                    pattern,
                    "[CODE_STRUCTURE_REMOVED]",
                    sanitized,
                )
                reasons.append("Removed code structure exposures")
                break

        return sanitized, " | ".join(reasons) if reasons else "No changes needed"

    def _get_safe_fallback(self) -> str:
        """Return safe fallback message when response must be blocked."""
        return (
            "I encountered a safety issue while processing your request and cannot provide a response. "
            "Please try rephrasing your question. If you believe this is in error, contact support."
        )

    def _get_explanation(self, unsafe_patterns: list, risk_level: str) -> str:
        """Generate human-readable explanation."""
        if not unsafe_patterns:
            return "Response is safe"

        if risk_level == "high":
            return f"Response contains high-risk unsafe patterns: {unsafe_patterns[0]}"
        elif risk_level == "medium":
            return f"Response contains medium-risk unsafe patterns: {unsafe_patterns[0]}"
        else:
            return f"Response contains low-risk patterns that should be reviewed: {unsafe_patterns[0]}"


# Global instance
_enforcer: Optional[ResponseEnforcer] = None


def get_response_enforcer() -> ResponseEnforcer:
    """Get or create response enforcer instance.

    Returns:
        ResponseEnforcer instance
    """
    global _enforcer
    if _enforcer is None:
        from app.core.config import settings

        # Get config from environment
        block_unsafe = getattr(settings, "ENFORCE_OUTPUT_VALIDATION", True)
        sanitize = getattr(settings, "SANITIZE_UNSAFE_RESPONSES", True)

        _enforcer = ResponseEnforcer(block_unsafe=block_unsafe, sanitize=sanitize)
    return _enforcer
