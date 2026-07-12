"""User SLO Profiles - Per-user tier-based SLO settings.

Allows different SLO thresholds for Premium, Standard, and Trial users.
Used by Phase 3.2 for tiered SLO enforcement.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class UserTier(str, Enum):
    """User tier classification."""

    TRIAL = "trial"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


@dataclass
class SLOThresholds:
    """SLO thresholds for a user tier."""

    # Latency thresholds (milliseconds)
    latency_target_ms: float  # p95 target
    latency_hard_limit_ms: float  # p99 hard limit
    latency_soft_warning_ms: float  # When to warn

    # Confidence thresholds
    confidence_min: float  # Minimum acceptable confidence (0.0-1.0)
    confidence_escalate_threshold: float  # When to escalate

    # Availability thresholds
    error_rate_max_percent: float  # Maximum acceptable error rate
    availability_slo_percent: float  # Availability SLO (e.g., 99.5%)

    # Query limits
    queries_per_hour: Optional[int] = None  # Rate limit per hour
    queries_per_day: Optional[int] = None  # Rate limit per day
    max_concurrent_queries: Optional[int] = None

    # Features
    allow_hybrid_routing: bool = True
    allow_sql_routing: bool = True
    allow_rag_routing: bool = True
    enable_caching: bool = True
    enable_background_evaluation: bool = False

    # Enforcement
    enforce_hard_limits: bool = True  # Reject on hard limit
    enforce_soft_limits: bool = True  # Warn on soft limit
    enable_circuit_breaker: bool = False


# Predefined tier thresholds
TIER_PROFILES = {
    UserTier.TRIAL: SLOThresholds(
        latency_target_ms=3000.0,  # Relaxed target
        latency_hard_limit_ms=8000.0,
        latency_soft_warning_ms=6000.0,
        confidence_min=0.40,  # Lower bar
        confidence_escalate_threshold=0.20,
        error_rate_max_percent=5.0,
        availability_slo_percent=95.0,
        queries_per_hour=50,
        queries_per_day=500,
        max_concurrent_queries=5,
        allow_hybrid_routing=False,
        allow_sql_routing=True,
        allow_rag_routing=True,
        enable_caching=False,
        enable_background_evaluation=False,
        enforce_hard_limits=False,  # Relaxed enforcement
        enforce_soft_limits=True,
        enable_circuit_breaker=False,
    ),
    UserTier.STANDARD: SLOThresholds(
        latency_target_ms=2500.0,
        latency_hard_limit_ms=5000.0,
        latency_soft_warning_ms=3500.0,
        confidence_min=0.50,
        confidence_escalate_threshold=0.30,
        error_rate_max_percent=2.0,
        availability_slo_percent=98.0,
        queries_per_hour=200,
        queries_per_day=5000,
        max_concurrent_queries=20,
        allow_hybrid_routing=True,
        allow_sql_routing=True,
        allow_rag_routing=True,
        enable_caching=True,
        enable_background_evaluation=False,
        enforce_hard_limits=True,
        enforce_soft_limits=True,
        enable_circuit_breaker=False,
    ),
    UserTier.PREMIUM: SLOThresholds(
        latency_target_ms=2000.0,  # Tight target
        latency_hard_limit_ms=3500.0,
        latency_soft_warning_ms=2800.0,
        confidence_min=0.60,  # High bar
        confidence_escalate_threshold=0.40,
        error_rate_max_percent=0.5,
        availability_slo_percent=99.5,
        queries_per_hour=1000,
        queries_per_day=50000,
        max_concurrent_queries=100,
        allow_hybrid_routing=True,
        allow_sql_routing=True,
        allow_rag_routing=True,
        enable_caching=True,
        enable_background_evaluation=True,
        enforce_hard_limits=True,
        enforce_soft_limits=True,
        enable_circuit_breaker=True,
    ),
    UserTier.ENTERPRISE: SLOThresholds(
        latency_target_ms=1500.0,  # Very tight
        latency_hard_limit_ms=2500.0,
        latency_soft_warning_ms=2000.0,
        confidence_min=0.70,
        confidence_escalate_threshold=0.50,
        error_rate_max_percent=0.1,
        availability_slo_percent=99.9,
        queries_per_hour=None,  # Unlimited
        queries_per_day=None,
        max_concurrent_queries=500,
        allow_hybrid_routing=True,
        allow_sql_routing=True,
        allow_rag_routing=True,
        enable_caching=True,
        enable_background_evaluation=True,
        enforce_hard_limits=True,
        enforce_soft_limits=True,
        enable_circuit_breaker=True,
    ),
}


class UserSLOProfileManager:
    """Manage per-user SLO profiles."""

    def __init__(self):
        """Initialize profile manager."""
        self.custom_profiles: Dict[str, SLOThresholds] = {}

    def get_user_tier(self, user_id: str) -> UserTier:
        """Get user's tier.

        Args:
            user_id: User identifier

        Returns:
            UserTier for this user

        Note:
            This is a placeholder - in production, query user database.
        """
        # Placeholder: would query user database
        # For now, default to STANDARD
        return UserTier.STANDARD

    def get_profile(self, user_id: str) -> SLOThresholds:
        """Get SLO profile for a user.

        Args:
            user_id: User identifier

        Returns:
            SLOThresholds for this user
        """
        # Check for custom profile first
        if user_id in self.custom_profiles:
            return self.custom_profiles[user_id]

        # Get tier-based profile
        tier = self.get_user_tier(user_id)
        return TIER_PROFILES.get(tier, TIER_PROFILES[UserTier.STANDARD])

    def set_custom_profile(self, user_id: str, profile: SLOThresholds):
        """Set custom SLO profile for a user.

        Args:
            user_id: User identifier
            profile: Custom SLOThresholds
        """
        self.custom_profiles[user_id] = profile

    def get_latency_threshold(self, user_id: str) -> Dict[str, float]:
        """Get latency thresholds for user.

        Args:
            user_id: User identifier

        Returns:
            {
                "target_ms": 2000,
                "soft_warning_ms": 2800,
                "hard_limit_ms": 5000,
            }
        """
        profile = self.get_profile(user_id)
        return {
            "target_ms": profile.latency_target_ms,
            "soft_warning_ms": profile.latency_soft_warning_ms,
            "hard_limit_ms": profile.latency_hard_limit_ms,
        }

    def get_confidence_threshold(self, user_id: str) -> Dict[str, float]:
        """Get confidence thresholds for user.

        Args:
            user_id: User identifier

        Returns:
            {
                "minimum": 0.50,
                "escalate_below": 0.30,
            }
        """
        profile = self.get_profile(user_id)
        return {
            "minimum": profile.confidence_min,
            "escalate_below": profile.confidence_escalate_threshold,
        }

    def get_rate_limits(self, user_id: str) -> Dict[str, Optional[int]]:
        """Get rate limits for user.

        Args:
            user_id: User identifier

        Returns:
            {
                "queries_per_hour": 200,
                "queries_per_day": 5000,
                "concurrent_queries": 20,
            }
        """
        profile = self.get_profile(user_id)
        return {
            "queries_per_hour": profile.queries_per_hour,
            "queries_per_day": profile.queries_per_day,
            "concurrent_queries": profile.max_concurrent_queries,
        }

    def is_within_limits(self, user_id: str, latency_ms: float, confidence: float) -> Dict[str, Any]:
        """Check if query meets user's SLO limits.

        Args:
            user_id: User identifier
            latency_ms: Query latency in milliseconds
            confidence: Confidence score (0.0-1.0)

        Returns:
            {
                "within_limits": bool,
                "latency_ok": bool,
                "confidence_ok": bool,
                "actions": [],  # Enforcement actions
            }
        """
        profile = self.get_profile(user_id)

        latency_ok = latency_ms <= profile.latency_target_ms
        confidence_ok = confidence >= profile.confidence_min

        within_limits = latency_ok and confidence_ok
        actions = []

        if not latency_ok and latency_ms > profile.latency_hard_limit_ms:
            actions.append("reject")
        elif not latency_ok and latency_ms > profile.latency_soft_warning_ms:
            actions.append("warn")

        if not confidence_ok and confidence < profile.confidence_escalate_threshold:
            actions.append("escalate")
        elif not confidence_ok:
            actions.append("warn")

        return {
            "within_limits": within_limits,
            "latency_ok": latency_ok,
            "confidence_ok": confidence_ok,
            "actions": actions,
        }

    def get_profile_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of user's SLO profile.

        Args:
            user_id: User identifier

        Returns:
            User profile summary
        """
        tier = self.get_user_tier(user_id)
        profile = self.get_profile(user_id)

        return {
            "user_id": user_id,
            "tier": tier.value,
            "latency_targets": {
                "target_ms": profile.latency_target_ms,
                "warning_ms": profile.latency_soft_warning_ms,
                "hard_limit_ms": profile.latency_hard_limit_ms,
            },
            "confidence_thresholds": {
                "minimum": profile.confidence_min,
                "escalate_below": profile.confidence_escalate_threshold,
            },
            "availability_slo": profile.availability_slo_percent,
            "rate_limits": {
                "per_hour": profile.queries_per_hour,
                "per_day": profile.queries_per_day,
                "concurrent": profile.max_concurrent_queries,
            },
            "features": {
                "hybrid_routing": profile.allow_hybrid_routing,
                "sql_routing": profile.allow_sql_routing,
                "rag_routing": profile.allow_rag_routing,
                "caching": profile.enable_caching,
                "background_evaluation": profile.enable_background_evaluation,
                "circuit_breaker": profile.enable_circuit_breaker,
            },
            "enforcement": {
                "hard_limits": profile.enforce_hard_limits,
                "soft_limits": profile.enforce_soft_limits,
            },
        }


# Global instance
_profile_manager: Optional[UserSLOProfileManager] = None


def get_user_slo_profile_manager() -> UserSLOProfileManager:
    """Get or create global profile manager."""
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = UserSLOProfileManager()
    return _profile_manager


def get_user_profile(user_id: str) -> SLOThresholds:
    """Get SLO profile for a user.

    Args:
        user_id: User identifier

    Returns:
        SLOThresholds for this user
    """
    manager = get_user_slo_profile_manager()
    return manager.get_profile(user_id)


def check_user_limits(user_id: str, latency_ms: float, confidence: float) -> Dict[str, Any]:
    """Check if query meets user's SLO limits.

    Args:
        user_id: User identifier
        latency_ms: Query latency in milliseconds
        confidence: Confidence score

    Returns:
        Limit check result
    """
    manager = get_user_slo_profile_manager()
    return manager.is_within_limits(user_id, latency_ms, confidence)
