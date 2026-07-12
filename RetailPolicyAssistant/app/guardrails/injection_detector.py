"""Injection Detector - Layer 4: Detects injection attacks.

This module provides backward-compatible detection with optional semantic/LLM-based
analysis to avoid false positives on legitimate policy questions.

Configuration:
  GUARDRAILS_SEMANTIC_INJECTION: Enable LLM-based detection (default: false)
  SEMANTIC_INJECTION_THRESHOLD: Score threshold to block (default: 0.8)
"""

import re
from typing import Dict, Optional
import logging

logger = logging.getLogger("injection_detector")


class InjectionDetector:
    """Detects injection attack attempts with optional semantic analysis.

    Combined approach:
    1. Fast pattern matching for obvious SQL/shell injection
    2. Optional semantic scoring for sophisticated jailbreaks
    3. Fallback to lightweight heuristic if LLM unavailable
    """

    # SQL injection patterns - NARROWED to reduce false positives
    SQL_INJECTION_PATTERNS = [
        # Stacked queries: ; followed by SQL command
        r";\s*(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b",
        # Boolean-based injection: OR 1=1 or OR 1='1'
        r"\bOR\s+\d+\s*=\s*\d+\b",
        r"\bOR\s+'\w+'\s*=\s*'\w+'\b",
        # Union-based injection
        r"\bUNION\s+ALL?\s+SELECT\b",
        # Comment-based injection
        r"(--\s+|#\s+|/\*.*?\*/)",
        # Time-based blind injection
        r"(WAITFOR|SLEEP|BENCHMARK)",
    ]

    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r"`.*`",  # Backticks for command execution
        r"\$\(.*\)",  # Command substitution
        r"[;&|]\s*(rm|cat|ls|curl|wget|bash|sh|cmd)",
    ]

    def __init__(self, use_semantic: bool = False):
        """Initialize injection detector.

        Args:
            use_semantic: If True, try to use semantic/LLM analysis
        """
        self.use_semantic = use_semantic
        self._semantic_detector = None

        if use_semantic:
            try:
                from app.guardrails.semantic_injection_detector import (
                    get_semantic_injection_detector,
                )

                self._semantic_detector = get_semantic_injection_detector(
                    enable_semantic=True
                )
            except ImportError:
                logger.warning(
                    "Semantic injection detector not available. Falling back to pattern matching."
                )
                self.use_semantic = False

    def check(self, text: str) -> Dict:
        """Check for injection attempts.

        Args:
            text: Query text to analyze

        Returns:
            {
                "has_injection": bool,
                "injections": list[str],
                "injection_score": float (if semantic enabled),
                "severity": str (if semantic enabled),
            }
        """
        # Try semantic detection first if enabled
        if self.use_semantic and self._semantic_detector:
            try:
                result = self._semantic_detector.check(text)
                return {
                    "has_injection": result.get("has_injection", False),
                    "injections": result.get("injections", []),
                    "injection_score": result.get("injection_score", 0.0),
                    "severity": result.get("severity", "none"),
                    "recommended_action": result.get("recommended_action", "allow"),
                }
            except Exception as e:
                logger.warning(f"Semantic injection check failed: {e}. Falling back.")

        # Fallback: Fast pattern matching
        injections = []

        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                injections.append(f"SQL injection pattern detected")
                break  # Only report once

        for pattern in self.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, text):
                injections.append(f"Command injection pattern detected")
                break  # Only report once

        return {
            "has_injection": len(injections) > 0,
            "injections": injections,
        }
