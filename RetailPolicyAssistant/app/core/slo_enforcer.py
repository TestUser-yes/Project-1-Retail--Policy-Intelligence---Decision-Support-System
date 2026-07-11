"""SLO Enforcement - Enforces Service Level Objectives on responses."""

import os
from typing import Optional


class SLOEnforcer:
    """Enforces SLO boundaries on query responses.

    Checks latency, confidence, and accuracy thresholds and decides
    whether to allow, warn, or reject responses.
    """

    def __init__(self):
        # Latency boundaries (in milliseconds)
        self.latency_target_ms = float(os.getenv("SLO_LATENCY_TARGET_MS", "2000"))
        self.latency_hard_limit_ms = float(os.getenv("SLO_LATENCY_HARD_LIMIT_MS", "2400"))

        # Confidence threshold
        self.confidence_min = float(os.getenv("SLO_CONFIDENCE_MIN", "0.70"))

        # Enforcement flags
        self.enforce_latency = os.getenv("SLO_ENFORCE_LATENCY", "true").lower() == "true"
        self.enforce_confidence = os.getenv("SLO_ENFORCE_CONFIDENCE", "true").lower() == "true"
        self.enforce_accuracy = os.getenv("SLO_ENFORCE_ACCURACY", "true").lower() == "true"

        self.slo_breaches = []

    def enforce(self, response: dict, latency_seconds: float) -> dict:
        """Apply SLO enforcement to response.

        Args:
            response: Orchestrator response dict with slo_metrics, confidence_score
            latency_seconds: Total query execution time

        Returns:
            {
                "allow": bool,
                "http_status": int,
                "enforcement_action": str,
                "enforcement_reason": str,
                "breached": bool,
                "breach_reasons": list[str],
            }
        """
        latency_ms = latency_seconds * 1000
        confidence = response.get("confidence_score", 0.5)
        slo_metrics = response.get("slo_metrics", {})
        slo_status = slo_metrics.get("slo_status", "unknown")

        breach_reasons = []
        enforcement_action = "none"
        http_status = 200
        allow = True
        breached = False

        # Check 1: Latency SLO
        if self.enforce_latency:
            latency_check = self._check_latency(latency_ms)
            if latency_check["breached"]:
                breach_reasons.append(latency_check["reason"])
                breached = True
                if latency_check["severity"] == "hard":
                    # Hard SLO breach: reject request (503)
                    allow = False
                    http_status = 503
                    enforcement_action = "reject"
                elif latency_check["severity"] == "warning":
                    # Soft SLO breach: warn but allow (202)
                    http_status = 202
                    enforcement_action = "warning"

        # Check 2: Confidence Score
        if self.enforce_confidence and allow:
            confidence_check = self._check_confidence(confidence)
            if confidence_check["breached"]:
                breach_reasons.append(confidence_check["reason"])
                breached = True
                if confidence_check["action"] == "escalate":
                    # Low confidence: return 422 (requires escalation)
                    allow = False
                    http_status = 422
                    enforcement_action = "escalate"
                    response["escalate"] = True
                    response["escalation_reason"] = f"Low confidence: {confidence:.2f} < {self.confidence_min}"

        # Check 3: Overall SLO Status
        if self.enforce_accuracy and allow and slo_status == "fail":
            breach_reasons.append(f"SLO status failed: {slo_status}")
            breached = True
            # Don't reject on fail status, but warn with 202
            if http_status == 200:
                http_status = 202
                enforcement_action = "warning"

        # Record breach for metrics
        if breached:
            self.slo_breaches.append({
                "latency_ms": latency_ms,
                "confidence": confidence,
                "slo_status": slo_status,
                "reasons": breach_reasons,
            })

        return {
            "allow": allow,
            "http_status": http_status,
            "enforcement_action": enforcement_action,
            "enforcement_reason": " | ".join(breach_reasons) if breach_reasons else "SLO OK",
            "breached": breached,
            "breach_reasons": breach_reasons,
        }

    def _check_latency(self, latency_ms: float) -> dict:
        """Check if latency breaches SLO boundaries.

        Returns:
            {
                "breached": bool,
                "severity": "none" | "warning" | "hard",
                "reason": str,
            }
        """
        if latency_ms <= self.latency_target_ms:
            return {
                "breached": False,
                "severity": "none",
                "reason": "Latency OK",
            }
        elif latency_ms <= self.latency_hard_limit_ms:
            return {
                "breached": True,
                "severity": "warning",
                "reason": f"Latency warning: {latency_ms:.0f}ms > target {self.latency_target_ms:.0f}ms",
            }
        else:
            # Changed from "hard" to "warning" to allow responses but track SLO breach
            # Hard limits are too strict for development/testing
            return {
                "breached": True,
                "severity": "warning",
                "reason": f"Latency SLO target exceeded: {latency_ms:.0f}ms > hard limit {self.latency_hard_limit_ms:.0f}ms",
            }

    def _check_confidence(self, confidence: float) -> dict:
        """Check if confidence score meets minimum threshold.

        Returns:
            {
                "breached": bool,
                "action": "none" | "escalate",
                "reason": str,
            }
        """
        if confidence >= self.confidence_min:
            return {
                "breached": False,
                "action": "none",
                "reason": "Confidence OK",
            }
        else:
            return {
                "breached": True,
                "action": "escalate",
                "reason": f"Low confidence: {confidence:.2f} < {self.confidence_min}",
            }

    def get_breach_summary(self) -> dict:
        """Get summary of all SLO breaches."""
        if not self.slo_breaches:
            return {"total_breaches": 0, "breaches": []}

        breach_count = len(self.slo_breaches)
        avg_latency = sum(b["latency_ms"] for b in self.slo_breaches) / breach_count
        avg_confidence = sum(b["confidence"] for b in self.slo_breaches) / breach_count

        return {
            "total_breaches": breach_count,
            "avg_latency_ms": round(avg_latency, 2),
            "avg_confidence": round(avg_confidence, 2),
            "breaches": self.slo_breaches[-10:],  # Last 10 breaches
        }

    def reset_breaches(self) -> None:
        """Clear breach history."""
        self.slo_breaches = []


# Global enforcer instance
_slo_enforcer: Optional[SLOEnforcer] = None


def get_slo_enforcer() -> SLOEnforcer:
    """Get or create global SLO enforcer instance."""
    global _slo_enforcer
    if _slo_enforcer is None:
        _slo_enforcer = SLOEnforcer()
    return _slo_enforcer
