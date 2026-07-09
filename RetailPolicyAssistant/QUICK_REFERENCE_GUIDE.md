# Quick Reference Guide - System Architecture

**Updated:** 2026-07-09  
**Status:** ✅ All Systems Operational

---

## 🎯 Critical Modules

### Cost Tracking (`app/core/cost_tracking.py`)
**Purpose:** Track query costs and enforce budget limits

**Usage:**
```python
from app.core.cost_tracking import get_cost_tracker

tracker = get_cost_tracker()

# Record a query
tracker.record_query(
    query_text="Your query here",
    query_id=None,  # Optional - set after DB save
    embedding_tokens=100,
    completion_tokens=50,
    embedding_cost=0.001,
    completion_cost=0.002
)

# Get summary
summary = tracker.get_summary()
print(f"Daily Cost: ${summary.daily_cost}")
print(f"Budget Remaining: ${summary.budget_remaining}")

# Check budget
status = tracker.check_budget()
print(f"Daily Limit OK: {status['daily_limit_ok']}")
```

**Budget Limits:**
- Daily: $100.00
- Monthly: $2000.00
- Per-Query: $1.00
- Alert Threshold: 80%

---

### SLO Tracking (`app/core/slo_tracker.py`)
**Purpose:** Monitor Service Level Objectives compliance

**Usage:**
```python
from app.core.slo_tracker import get_slo_tracker

slo_tracker = get_slo_tracker()

# Record latency
latency_seconds = 1.5
slo_metrics = slo_tracker.record_latency(latency_seconds)
print(f"Status: {slo_metrics.slo_status}")  # pass, warning, fail

# Record query outcome
slo_tracker.record_query_outcome(success=True)

# Record escalation
slo_tracker.record_escalation()

# Get summary
summary = slo_tracker.get_summary()
print(f"SLO Compliance: {summary['slo_compliance_rate_percent']}%")
```

**SLO Targets:**
- Task Success Rate: ≥90%
- P95 Latency: ≤3 seconds
- Route Accuracy: 95%
- Answer Accuracy: 90%
- Risk Classification: 95%
- Escalation Detection: 100%

---

### Orchestrator (`app/orchestrator.py`)
**Purpose:** Main query processing engine

**Flow:**
```python
from app.orchestrator import Orchestrator

orchestrator = Orchestrator(db=db)
response = orchestrator.run(query="What is the vendor approval policy?")

# Response structure:
{
    "query": str,
    "intent": {"intent": str, "reason": str},
    "route": "sql" | "rag" | "hybrid",
    "result": {"result": str},
    "risk": {"risk_level": "low" | "medium" | "high", "reason": str},
    "escalate": bool,
    "escalation_reason": str,
    "latency_seconds": float,
    "cost_usd": float,
    "budget_remaining_usd": float,
    "budget_percent_used": float,
    "slo_metrics": {
        "latency_ms": float,
        "target_latency_ms": float,
        "slo_status": str
    },
    "confidence_score": float,
    "sources": list,
    "sql_validation": str,
    "recommendation": str
}
```

---

## 🔄 Query Processing Pipeline

```
User Query
    ↓
[Input Validation] - Check length, content
    ↓
[Permission Check] - User has ASK_POLICY_QUESTION
    ↓
[Rate Limiting] - Within 100 requests/hour
    ↓
[Conversation Mgmt] - Create/retrieve conversation
    ↓
[Orchestrator] - Main processing
    ├─→ Relevance Check - Is it about policies/vendors?
    ├─→ Intent Detection - SQL/RAG/Hybrid?
    ├─→ Route Selection - Choose handler
    ├─→ Query Execution - Run handler
    ├─→ Token Counting - Count embeddings/completions
    ├─→ Risk Assessment - low/medium/high?
    ├─→ Escalation Check - Needs human review?
    ├─→ Cost Tracking - Record costs ✅ FIXED
    └─→ SLO Tracking - Record metrics
    ↓
[Response Formatting] - Build AskResponse
    ↓
[Database Save] - Store to ai_queries table
    ↓
[Conversation Memory] - Add to conversation history
    ↓
Client Response
```

---

## 🐛 Recent Fixes

### Fix 1: CostTracker.record_query() Parameter
**Issue:** Missing `query_id` parameter causing error fallback

**Fix Applied:**
```python
# File: app/orchestrator.py, Line 101-108
self.cost_tracker.record_query(
    query_text=query,
    query_id=None,  # ← ADDED - Now explicitly provided
    embedding_tokens=embedding_tokens,
    completion_tokens=completion_tokens,
    embedding_cost=embedding_cost,
    completion_cost=completion_cost,
)
```

**Status:** ✅ FIXED

---

## 📊 Configuration Overview

### Intent Keywords (from `config_loader.py`)
```python
Policy Keywords: policy, procedure, rule, guideline, process, protocol, ...
Vendor Keywords: vendor, supplier, partner, cost, price, budget, contract, ...
Retail Keywords: refund, return, customer, employee, promotion, inventory, ...
```

### Risk Thresholds
```python
Low Risk:
  - confidence_min: 0.8
  - keywords: []

Medium Risk:
  - confidence_min: 0.5
  - keywords: approval, compliance, audit, finding, ...

High Risk:
  - confidence_min: 0.0
  - keywords: override, violation, critical, breach, ...
```

### Rate Limits
```python
Per User: 100 requests/hour
Global: 1000 requests/hour
```

### Query Constraints
```python
Min Length: 3 characters
Max Length: 10,000 characters
```

---

## 📁 Key Files Location

| Component | File Path |
|-----------|-----------|
| Cost Tracking | `app/core/cost_tracking.py` |
| SLO Tracking | `app/core/slo_tracker.py` |
| Main Orchestrator | `app/orchestrator.py` |
| API Endpoints | `app/api.py` |
| Configuration | `app/config/config_loader.py` |
| Constants | `app/config/constants.py` |
| RAG Agent | `app/agents/rag_agent.py` |
| SQL Agent | `app/agents/sql_agent.py` |
| Database Models | `app/models/ai_queries.py` |
| Auth System | `app/core/auth.py` |
| Rate Limiter | `app/core/rate_limit.py` |
| Guardrails | `app/core/guardrails.py` |

---

## 🚀 Getting Started

### 1. Start the Server
```bash
cd RetailPolicyAssistant
python main.py
```

### 2. Get Token
```bash
curl http://localhost:8000/token
# Returns: {"access_token": "demo-token", "token_type": "bearer"}
```

### 3. Ask a Query
```bash
curl -X POST http://localhost:8000/ask \
  -H "Authorization: Bearer demo-token" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is our vendor approval policy?"}'
```

### 4. Check Health
```bash
curl http://localhost:8000/health
```

---

## 🔍 Debugging Tips

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Cost Tracking
```python
from app.core.cost_tracking import get_cost_tracker
tracker = get_cost_tracker()
print(tracker.get_cost_report())
```

### Check SLO Status
```python
from app.core.slo_tracker import get_slo_tracker
slo = get_slo_tracker()
print(slo.get_summary())
```

### Trace Query Execution
```bash
# Check Langfuse tracing at:
# http://localhost:3000 (if Langfuse is running locally)
```

---

## 📈 Performance Targets

| Metric | Target |
|--------|--------|
| P95 Latency | ≤3 seconds |
| Average Latency | 2 seconds |
| Success Rate | ≥90% |
| Route Accuracy | 95% |
| Risk Classification | 95% |
| Escalation Detection | 100% |
| SLO Compliance | ≥90% |

---

## ⚠️ Common Issues & Solutions

### Issue: "CostTracker.record_query() missing parameter"
**Solution:** Already fixed! Make sure you have the latest code deployed.

### Issue: Queries failing with error fallback
**Check:**
1. Database connection (✓ Verified)
2. API permissions (use `/token` endpoint)
3. Query format (min 3 chars, max 10,000)
4. Rate limits (check `/ask` endpoint)

### Issue: High latency (>3 seconds)
**Check:**
1. RAG retriever response time
2. Database query performance
3. Token counting overhead
4. Network latency to LLM

### Issue: Budget exceeded
**Check:**
1. Token counting accuracy
2. Cost configuration (check if using expensive models)
3. Query volume surge
4. Token wastage in prompts

---

## 🔐 Security Checklist

- ✅ Authentication required for `/ask` endpoint
- ✅ Rate limiting per user
- ✅ Input validation and sanitization
- ✅ SQL injection prevention in queries
- ✅ PII detection in responses
- ✅ Toxicity filtering
- ✅ Permission-based access control

---

## 📚 Related Documentation

- [System Audit Report](SYSTEM_AUDIT_AND_FIX_REPORT.md) - Comprehensive system analysis
- [README.md](README.md) - Project overview
- [Architecture Docs](docs/) - Detailed architecture

---

**Last Updated:** 2026-07-09  
**System Status:** ✅ OPERATIONAL  
**Contact:** Retail Policy Intelligence Team
