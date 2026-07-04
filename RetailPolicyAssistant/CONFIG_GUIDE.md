# Dynamic Configuration Guide

## Overview

The Retail Policy Intelligence system now uses a comprehensive dynamic configuration system. All hardcoded values have been replaced with configurable settings that can be customized via:

1. **YAML/JSON Configuration Files** (highest priority in file system)
2. **Environment Variables** (override file settings)
3. **Defaults** (fallback values)

---

## Configuration File

### Location
```
RetailPolicyAssistant/config/system.yaml
```

### Structure

The configuration file has the following sections:

#### 1. Keywords Configuration
Controls which keywords trigger different intent detection routes.

```yaml
keywords:
  policy:
    - policy
    - procedure
    - rule
    # ... full list in system.yaml
  vendor:
    - vendor
    - supplier
    - partner
    # ... full list in system.yaml
  retail:
    - refund
    - return
    - exchange
    # ... full list in system.yaml
```

**Usage:** Customize keywords for your specific domain or language requirements.

#### 2. Risk Thresholds Configuration
Defines risk levels (low, medium, high) and associated keywords.

```yaml
risk_thresholds:
  low:
    confidence_min: 0.8
    keywords: []  # Low-risk queries have no keywords
  
  medium:
    confidence_min: 0.5
    keywords:
      - approval
      - compliance
      - audit
      # ... more keywords
  
  high:
    confidence_min: 0.0
    keywords:
      - override
      - violation
      - critical
      - legal hold
      # ... more keywords
```

**Usage:**
- Queries with HIGH-RISK keywords trigger escalation to compliance review
- Queries with MEDIUM-RISK keywords trigger additional validation
- All other queries are LOW-RISK

#### 3. Cost Configuration
Defines pricing for different LLM providers.

```yaml
cost:
  provider: ollama  # ollama, openai, anthropic
  embedding_cost_per_1k: 0.0  # Cost per 1,000 tokens
  completion_cost_per_1k: 0.0  # Cost per 1,000 tokens
  budget_usd: 100.0  # Monthly budget
```

**Usage:**
- Set provider to track which LLM is being used
- Update costs when switching providers
- Monitor budget usage in SLO metrics

#### 4. Authentication Configuration
Controls demo user credentials and JWT settings.

```yaml
auth:
  secret_key: ${SECRET_KEY:-demo-secret-key-change-in-production}
  algorithm: HS256
  access_token_expire_minutes: 30
  
  # Demo user credentials
  demo_user_id: demo-user
  demo_username: demo
  demo_email: demo@retailpolicy.local
  demo_role: user
  
  # Admin credentials
  admin_user_id: demo-admin
  admin_username: admin
  admin_email: admin@retailpolicy.local
  admin_role: admin
```

**Usage:**
- Change demo credentials for different testing scenarios
- Adjust token expiration as needed
- Environment variable `SECRET_KEY` overrides file value

#### 5. Routing Configuration
Determines routing strategy (keyword-based or LLM-based).

```yaml
routing:
  intent_strategy: keywords  # keywords or llm
  risk_assessment_strategy: keywords  # keywords or llm
```

**Usage:**
- `keywords`: Fast, rule-based routing
- `llm`: Advanced LLM-based routing (requires LLM service)

---

## Environment Variables

Override any configuration value using environment variables:

### Authentication
```bash
export SECRET_KEY="your-secret-key-here"
export DEMO_USER_ID="your-demo-user-id"
export DEMO_USERNAME="your-demo-username"
export DEMO_EMAIL="your-demo-email@company.com"
export DEMO_ROLE="user"
```

### Cost Tracking
```bash
export LLM_PROVIDER="openai"  # or "anthropic", "ollama"
export EMBEDDING_COST_1K="0.0001"  # Cost per 1,000 tokens
export COMPLETION_COST_1K="0.0002"  # Cost per 1,000 tokens
export BUDGET_USD="500.0"  # Monthly budget
```

### Routing Strategy
```bash
export INTENT_STRATEGY="keywords"  # or "llm"
export RISK_ASSESSMENT_STRATEGY="keywords"  # or "llm"
```

---

## Usage Examples

### Example 1: OpenAI Provider with Costs

**Environment Variables:**
```bash
export LLM_PROVIDER="openai"
export EMBEDDING_COST_1K="0.0001"
export COMPLETION_COST_1K="0.002"
export BUDGET_USD="1000.0"
```

The system will now:
- Track costs for OpenAI API calls
- Calculate embedding costs at $0.0001 per 1k tokens
- Calculate completion costs at $0.002 per 1k tokens
- Monitor against $1000 monthly budget

### Example 2: Custom Keywords for Specific Domain

**config/system.yaml:**
```yaml
keywords:
  policy:
    - policy
    - procedure
    - gdpr
    - hipaa
    - pci-dss
  vendor:
    - vendor
    - supplier
    - 3pl
    - partner
```

Now queries about GDPR/HIPAA/PCI-DSS will be routed to RAG (policy) analysis.

### Example 3: Stricter Risk Thresholds

**config/system.yaml:**
```yaml
risk_thresholds:
  high:
    keywords:
      - override
      - violation
      - critical
      - legal hold
      - suspend
      - reject
      - urgent
      - escalation
```

More keywords trigger HIGH-RISK escalation, increasing compliance review.

### Example 4: Multiple Profiles (Dev/Staging/Prod)

**Environment Files:**

`.env.development`:
```bash
LLM_PROVIDER=ollama
EMBEDDING_COST_1K=0.0
COMPLETION_COST_1K=0.0
BUDGET_USD=100.0
```

`.env.production`:
```bash
LLM_PROVIDER=anthropic
EMBEDDING_COST_1K=0.0003
COMPLETION_COST_1K=0.0015
BUDGET_USD=10000.0
```

Load appropriate file based on environment:
```bash
source .env.${ENVIRONMENT}
python -m app.main
```

---

## Accessing Configuration in Code

### In Application Code

```python
from app.config import get_config

# Get the global config instance
config = get_config()

# Access specific sections
policy_keywords = config.keywords.policy
risk_high_keywords = config.risk_thresholds.high["keywords"]
provider = config.cost.provider
secret_key = config.auth.secret_key

# Reload configuration if changed
from app.config import reload_config
config = reload_config()
```

### In Orchestrator

```python
class Orchestrator:
    def __init__(self, db):
        self.config = get_config()
        self.policy_keywords = self.config.keywords.policy
        self.risk_thresholds = self.config.risk_thresholds
        self.cost_config = self.config.cost
```

---

## Adding New Configuration Options

### Step 1: Update Data Classes

Edit `app/config/config_loader.py`:

```python
@dataclass
class MyNewConfig:
    """New configuration section."""
    setting_1: str = "default_value"
    setting_2: int = 100

@dataclass
class SystemConfig:
    # ... existing configs ...
    my_new_config: MyNewConfig = None
    
    def __post_init__(self):
        # ... existing inits ...
        if self.my_new_config is None:
            self.my_new_config = MyNewConfig()
```

### Step 2: Update Config File

Edit `config/system.yaml`:

```yaml
my_new_config:
  setting_1: "my_value"
  setting_2: 42
```

### Step 3: Use in Code

```python
config = get_config()
value = config.my_new_config.setting_1
```

---

## Configuration Validation

The configuration system includes type hints and data classes for validation:

```python
# This will raise an error if the type doesn't match
cost_config = CostConfig(
    provider="invalid_provider",  # Still accepted (string)
    budget_usd="not_a_number",    # Type error if strict validation added
)
```

To add strict validation, create a validation method:

```python
def validate_config(config: SystemConfig) -> bool:
    """Validate configuration."""
    valid_providers = ["ollama", "openai", "anthropic"]
    if config.cost.provider not in valid_providers:
        raise ValueError(f"Invalid provider: {config.cost.provider}")
    
    if config.cost.budget_usd < 0:
        raise ValueError("Budget cannot be negative")
    
    return True
```

---

## Troubleshooting

### Config Not Loading

**Problem:** Changes to `system.yaml` aren't reflected.

**Solution:** Call `reload_config()` after file changes:
```python
from app.config import reload_config
config = reload_config()
```

### Environment Variable Not Working

**Problem:** Environment variable is set but not being used.

**Solution:** Check variable naming and section:
```bash
# Correct
export SECRET_KEY="my-secret"

# Wrong (different sections)
export KEYWORD_POLICY="policy"  # No effect
```

### Type Errors

**Problem:** Configuration values have wrong types.

**Solution:** Check data class definitions and ensure file values match:
```yaml
cost:
  budget_usd: 100.0  # Must be float, not string
  embedding_cost_per_1k: 0.0001  # Must be float
```

---

## Migration from Hardcoded Values

### Before (Hardcoded)
```python
SECRET_KEY = "demo-secret-key-change-in-production"
POLICY_KEYWORDS = ["policy", "procedure", ...]
risk_level = "high" if not is_relevant else "low"
```

### After (Dynamic)
```python
from app.config import get_config

config = get_config()
SECRET_KEY = config.auth.secret_key
POLICY_KEYWORDS = config.keywords.policy
risk_level = orchestrator._assess_risk_level(query, is_relevant)
```

---

## Best Practices

1. **Use Config Files for Static Settings**
   - Keywords, thresholds, cost parameters
   - Commit to version control

2. **Use Environment Variables for Secrets**
   - SECRET_KEY, API credentials
   - Different per environment
   - Don't commit to version control

3. **Override Hierarchy**
   - Environment variables always override file settings
   - File settings override defaults
   - Defaults are fallback

4. **Document Custom Settings**
   - Add comments in system.yaml
   - Update this guide with new options
   - Provide examples

5. **Validate on Startup**
   - Add validation in application initialization
   - Fail fast if config is invalid
   - Provide clear error messages

---

## Configuration Reload at Runtime

The system supports reloading configuration without restart:

```python
from app.config import reload_config

# After modifying config/system.yaml or environment variables
new_config = reload_config()

# Update orchestrator with new config
orchestrator.config = new_config
orchestrator.policy_keywords = new_config.keywords.policy
```

---

## Support for Multiple Environments

Create environment-specific config files:

```
config/
├── system.yaml              # Default
├── system.development.yaml  # Development overrides
├── system.staging.yaml      # Staging overrides
└── system.production.yaml   # Production overrides
```

Load based on environment:

```python
import os
env = os.getenv("APP_ENV", "development")
config_file = f"system.{env}.yaml"
config = loader.load(config_file)
```

---

