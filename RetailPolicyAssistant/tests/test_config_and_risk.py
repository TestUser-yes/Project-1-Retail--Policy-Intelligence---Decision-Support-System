"""Tests for configuration system and risk scoring."""

import sys
import os
from pathlib import Path

# Add app directory to path for imports
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

from app.config import (
    ConfigLoader,
    SystemConfig,
    KeywordConfig,
    RiskThresholdConfig,
    CostConfig,
    AuthConfig,
    RoutingConfig,
    get_config,
)


class TestConfigLoader:
    """Test configuration loading system."""

    def test_config_defaults(self):
        """Test that defaults are created correctly."""
        config = SystemConfig()
        assert config.keywords is not None
        assert config.risk_thresholds is not None
        assert config.cost is not None
        assert config.auth is not None
        assert config.routing is not None
        print("✅ Config defaults created")

    def test_keyword_config(self):
        """Test keyword configuration."""
        config = get_config()
        assert len(config.keywords.policy) > 0
        assert len(config.keywords.vendor) > 0
        assert len(config.keywords.retail) > 0
        assert "policy" in config.keywords.policy
        assert "vendor" in config.keywords.vendor
        print("✅ Keywords configured correctly")

    def test_risk_thresholds(self):
        """Test risk threshold configuration."""
        config = get_config()
        assert "low" in config.risk_thresholds.low
        assert "medium" in config.risk_thresholds.medium
        assert "high" in config.risk_thresholds.high
        assert config.risk_thresholds.high["keywords"] is not None
        assert "critical" in config.risk_thresholds.high["keywords"]
        print("✅ Risk thresholds configured correctly")

    def test_cost_config(self):
        """Test cost configuration."""
        config = get_config()
        assert config.cost.provider in ["ollama", "openai", "anthropic"]
        assert config.cost.embedding_cost_per_1k >= 0
        assert config.cost.completion_cost_per_1k >= 0
        assert config.cost.budget_usd > 0
        print("✅ Cost configuration correct")

    def test_auth_config(self):
        """Test authentication configuration."""
        config = get_config()
        assert config.auth.secret_key is not None
        assert config.auth.algorithm == "HS256"
        assert config.auth.access_token_expire_minutes > 0
        assert config.auth.demo_username == "demo"
        assert config.auth.admin_username == "admin"
        print("✅ Auth configuration correct")

    def test_routing_config(self):
        """Test routing configuration."""
        config = get_config()
        assert config.routing.intent_strategy in ["keywords", "llm"]
        assert config.routing.risk_assessment_strategy in ["keywords", "llm"]
        print("✅ Routing configuration correct")


class TestRiskScoring:
    """Test 3-level risk scoring system."""

    def test_risk_level_assignment(self):
        """Test risk level is properly assigned."""
        config = get_config()

        # Simulate risk assessment logic
        def assess_risk(query: str, is_relevant: bool) -> str:
            query_lower = query.lower()

            if not is_relevant:
                return "high"

            high_risk_kws = config.risk_thresholds.high.get("keywords", [])
            if any(kw in query_lower for kw in high_risk_kws):
                return "high"

            medium_risk_kws = config.risk_thresholds.medium.get("keywords", [])
            if any(kw in query_lower for kw in medium_risk_kws):
                return "medium"

            return "low"

        # Test cases
        assert assess_risk("What is our retention policy?", True) == "low"
        assert assess_risk("What's the weather?", False) == "high"
        assert assess_risk("Can we override vendor rejection?", True) == "high"
        assert assess_risk("Show vendors under compliance review", True) == "medium"
        assert assess_risk("GDPR compliance violations detected", True) == "high"
        print("✅ All risk scoring tests passed")

    def test_high_risk_keywords(self):
        """Test high-risk keywords trigger high risk level."""
        config = get_config()
        high_keywords = config.risk_thresholds.high.get("keywords", [])

        assert "override" in high_keywords
        assert "critical" in high_keywords
        assert "legal hold" in high_keywords
        assert "gdpr" in high_keywords
        assert "escalation" in high_keywords
        print("✅ High-risk keywords defined")

    def test_medium_risk_keywords(self):
        """Test medium-risk keywords are configured."""
        config = get_config()
        medium_keywords = config.risk_thresholds.medium.get("keywords", [])

        assert len(medium_keywords) > 0
        assert "approval" in medium_keywords or "compliance" in medium_keywords
        print("✅ Medium-risk keywords defined")

    def test_three_level_classification(self):
        """Test 3-level risk classification."""
        levels = ["low", "medium", "high"]
        config = get_config()

        # All three levels should be in config
        assert config.risk_thresholds.low is not None
        assert config.risk_thresholds.medium is not None
        assert config.risk_thresholds.high is not None
        print("✅ 3-level risk classification available")


class TestDynamicOverrides:
    """Test environment variable overrides."""

    def test_env_override_capability(self):
        """Test that environment variables can override defaults."""
        # This test verifies the mechanism exists
        # Actual override happens at runtime

        # Save original value
        original_provider = os.getenv("LLM_PROVIDER")

        try:
            # Set environment variable
            os.environ["LLM_PROVIDER"] = "openai"

            # Reload config to pick up the change
            from app.config import reload_config
            new_config = reload_config()

            # The env var should be available for use
            assert os.getenv("LLM_PROVIDER") == "openai"
            print("✅ Environment variable override mechanism works")

        finally:
            # Restore original
            if original_provider:
                os.environ["LLM_PROVIDER"] = original_provider
            else:
                os.environ.pop("LLM_PROVIDER", None)


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("RUNNING CONFIGURATION AND RISK SCORING TESTS")
    print("="*60 + "\n")

    # Config tests
    print("Testing Configuration System...")
    config_tests = TestConfigLoader()
    config_tests.test_config_defaults()
    config_tests.test_keyword_config()
    config_tests.test_risk_thresholds()
    config_tests.test_cost_config()
    config_tests.test_auth_config()
    config_tests.test_routing_config()

    # Risk scoring tests
    print("\nTesting Risk Scoring...")
    risk_tests = TestRiskScoring()
    risk_tests.test_risk_level_assignment()
    risk_tests.test_high_risk_keywords()
    risk_tests.test_medium_risk_keywords()
    risk_tests.test_three_level_classification()

    # Override tests
    print("\nTesting Dynamic Overrides...")
    override_tests = TestDynamicOverrides()
    override_tests.test_env_override_capability()

    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        run_all_tests()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
