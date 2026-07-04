"""Configuration loader for dynamic system settings."""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class KeywordConfig:
    """Keyword configuration for intent detection."""
    policy: list = None
    vendor: list = None
    retail: list = None

    def __post_init__(self):
        if self.policy is None:
            self.policy = [
                "policy", "procedure", "rule", "guideline", "process",
                "protocol", "standard", "requirement", "compliance",
                "approval", "authorization", "permission", "access",
            ]
        if self.vendor is None:
            self.vendor = [
                "vendor", "supplier", "partner", "cost", "price",
                "budget", "rate", "fee", "contract", "invoice",
                "payment", "terms", "discount", "wholesale",
            ]
        if self.retail is None:
            self.retail = [
                "refund", "return", "exchange", "customer", "employee",
                "discount", "promotion", "sale", "inventory", "stock",
                "shipping", "delivery", "warehouse", "store", "outlet",
            ]


@dataclass
class RiskThresholdConfig:
    """Risk threshold configuration."""
    low: Dict[str, Any] = None
    medium: Dict[str, Any] = None
    high: Dict[str, Any] = None

    def __post_init__(self):
        if self.low is None:
            self.low = {
                "confidence_min": 0.8,
                "keywords": [],
            }
        if self.medium is None:
            self.medium = {
                "confidence_min": 0.5,
                "keywords": [
                    "approval", "compliance", "audit", "finding",
                    "remediation", "pending", "under review", "cross-border",
                ],
            }
        if self.high is None:
            self.high = {
                "confidence_min": 0.0,
                "keywords": [
                    "override", "violation", "critical", "legal hold",
                    "gdpr", "escalation", "non-compliant", "breach",
                    "restriction", "suspended", "rejected", "urgent",
                ],
            }


@dataclass
class CostConfig:
    """Cost tracking configuration."""
    provider: str = "ollama"  # ollama, openai, anthropic
    embedding_cost_per_1k: float = 0.0
    completion_cost_per_1k: float = 0.0
    budget_usd: float = 100.0


@dataclass
class AuthConfig:
    """Authentication configuration."""
    secret_key: str = None
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    demo_user_id: str = "demo-user"
    demo_username: str = "demo"
    demo_email: str = "demo@retailpolicy.local"
    demo_role: str = "user"
    admin_user_id: str = "demo-admin"
    admin_username: str = "admin"
    admin_email: str = "admin@retailpolicy.local"
    admin_role: str = "admin"

    def __post_init__(self):
        if self.secret_key is None:
            self.secret_key = os.getenv(
                "SECRET_KEY",
                "demo-secret-key-change-in-production"
            )


@dataclass
class RoutingConfig:
    """Query routing configuration."""
    intent_strategy: str = "keywords"  # keywords, llm
    risk_assessment_strategy: str = "keywords"  # keywords, llm


@dataclass
class SystemConfig:
    """Main system configuration."""
    keywords: KeywordConfig = None
    risk_thresholds: RiskThresholdConfig = None
    cost: CostConfig = None
    auth: AuthConfig = None
    routing: RoutingConfig = None

    def __post_init__(self):
        if self.keywords is None:
            self.keywords = KeywordConfig()
        if self.risk_thresholds is None:
            self.risk_thresholds = RiskThresholdConfig()
        if self.cost is None:
            self.cost = CostConfig()
        if self.auth is None:
            self.auth = AuthConfig()
        if self.routing is None:
            self.routing = RoutingConfig()


class ConfigLoader:
    """Load configuration from YAML/JSON files or environment variables."""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)

    def load(self, config_file: Optional[str] = None) -> SystemConfig:
        """
        Load configuration from file or environment.

        Priority:
        1. Config file (YAML/JSON)
        2. Environment variables
        3. Defaults
        """
        # Start with defaults
        config = SystemConfig()

        # Override with file if provided
        if config_file and (self.config_dir / config_file).exists():
            config = self._load_from_file(config_file)
        else:
            # Try to load from default files
            if (self.config_dir / "system.yaml").exists():
                config = self._load_from_file("system.yaml")
            elif (self.config_dir / "system.json").exists():
                config = self._load_from_file("system.json")

        # Override with environment variables
        config = self._override_with_env(config)

        return config

    def _load_from_file(self, filename: str) -> SystemConfig:
        """Load configuration from YAML or JSON file."""
        filepath = self.config_dir / filename

        try:
            with open(filepath, "r") as f:
                if filename.endswith(".yaml") or filename.endswith(".yml"):
                    data = yaml.safe_load(f) or {}
                else:
                    data = json.load(f)

            # Parse configuration sections
            keywords = KeywordConfig(**data.get("keywords", {}))
            risk_thresholds = RiskThresholdConfig(**data.get("risk_thresholds", {}))
            cost = CostConfig(**data.get("cost", {}))
            auth = AuthConfig(**data.get("auth", {}))
            routing = RoutingConfig(**data.get("routing", {}))

            return SystemConfig(
                keywords=keywords,
                risk_thresholds=risk_thresholds,
                cost=cost,
                auth=auth,
                routing=routing,
            )
        except Exception as e:
            print(f"Warning: Failed to load config from {filepath}: {e}")
            return SystemConfig()

    def _override_with_env(self, config: SystemConfig) -> SystemConfig:
        """Override configuration with environment variables."""
        # Auth overrides
        if os.getenv("SECRET_KEY"):
            config.auth.secret_key = os.getenv("SECRET_KEY")
        if os.getenv("DEMO_USER_ID"):
            config.auth.demo_user_id = os.getenv("DEMO_USER_ID")
        if os.getenv("DEMO_USERNAME"):
            config.auth.demo_username = os.getenv("DEMO_USERNAME")
        if os.getenv("DEMO_EMAIL"):
            config.auth.demo_email = os.getenv("DEMO_EMAIL")
        if os.getenv("DEMO_ROLE"):
            config.auth.demo_role = os.getenv("DEMO_ROLE")

        # Cost overrides
        if os.getenv("LLM_PROVIDER"):
            config.cost.provider = os.getenv("LLM_PROVIDER")
        if os.getenv("EMBEDDING_COST_1K"):
            config.cost.embedding_cost_per_1k = float(os.getenv("EMBEDDING_COST_1K"))
        if os.getenv("COMPLETION_COST_1K"):
            config.cost.completion_cost_per_1k = float(os.getenv("COMPLETION_COST_1K"))
        if os.getenv("BUDGET_USD"):
            config.cost.budget_usd = float(os.getenv("BUDGET_USD"))

        # Routing overrides
        if os.getenv("INTENT_STRATEGY"):
            config.routing.intent_strategy = os.getenv("INTENT_STRATEGY")
        if os.getenv("RISK_ASSESSMENT_STRATEGY"):
            config.routing.risk_assessment_strategy = os.getenv("RISK_ASSESSMENT_STRATEGY")

        return config

    def save_default_config(self, filename: str = "system.yaml"):
        """Save default configuration to file."""
        config = SystemConfig()
        filepath = self.config_dir / filename

        config_dict = {
            "keywords": asdict(config.keywords),
            "risk_thresholds": asdict(config.risk_thresholds),
            "cost": asdict(config.cost),
            "auth": asdict(config.auth),
            "routing": asdict(config.routing),
        }

        try:
            with open(filepath, "w") as f:
                if filename.endswith(".yaml") or filename.endswith(".yml"):
                    yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
                else:
                    json.dump(config_dict, f, indent=2)
            print(f"Default configuration saved to {filepath}")
        except Exception as e:
            print(f"Error saving config: {e}")

    def to_dict(self, config: SystemConfig) -> dict:
        """Convert config to dictionary."""
        return {
            "keywords": asdict(config.keywords),
            "risk_thresholds": asdict(config.risk_thresholds),
            "cost": asdict(config.cost),
            "auth": asdict(config.auth),
            "routing": asdict(config.routing),
        }


# Global config instance
_config_instance: Optional[SystemConfig] = None


def get_config() -> SystemConfig:
    """Get the global configuration instance."""
    global _config_instance
    if _config_instance is None:
        loader = ConfigLoader()
        _config_instance = loader.load()
    return _config_instance


def reload_config() -> SystemConfig:
    """Reload configuration."""
    global _config_instance
    loader = ConfigLoader()
    _config_instance = loader.load()
    return _config_instance
