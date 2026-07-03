# 🎯 DEMO READINESS COMPLETION PLAN

**Status:** ✅ Plan Created  
**Target:** All items FULLY COMPLETE for demo  
**Date:** 2026-07-03

---

## 📋 Gap Analysis from README Requirements

Based on README.md core requirements and current implementation audit:

### CRITICAL GAPS (Must Fix Before Demo)

| Gap | Current State | Required State | Priority | Effort |
|-----|---|---|---|---|
| **RBAC & Auth** | ❌ Missing | ✅ Auth middleware + permission checks | HIGH | 4h |
| **Cost Tracking** | ⚠️ Scaffolding only | ✅ Wired into orchestrator | MEDIUM | 2h |
| **Prompt Registry** | ⚠️ Scattered files | ✅ Centralized in app/prompts.py | MEDIUM | 1.5h |
| **Conversation Memory** | ❌ Missing | ✅ Context window manager | MEDIUM | 3h |
| **Trace Emission** | ⚠️ Model only | ✅ Actually emit traces | LOW | 1.5h |

---

## 🔧 COMPLETION TASKS

### PHASE 1: Security & Auth (Critical)

**Task 1.1: Create Auth Module**
- Location: `app/core/auth.py`
- Purpose: JWT token validation, user extraction
- Deliverables:
  - `verify_token()` function
  - `get_current_user()` dependency
  - User role extraction

**Task 1.2: Create Guardrails Module**
- Location: `app/core/guardrails.py`
- Purpose: Query validation, safety checks
- Deliverables:
  - `check_query_safety()` function
  - Sensitive data detection
  - Query sanitization

**Task 1.3: Add Auth Middleware**
- Location: Modify `app/main.py`
- Purpose: Apply auth to routes
- Deliverables:
  - Middleware registration
  - Token verification on `/ask`
  - Role-based access checks

---

### PHASE 2: Cost Tracking Integration (Medium Priority)

**Task 2.1: Wire Cost Tracker**
- Location: Modify `app/orchestrator.py`
- Purpose: Track costs per query
- Deliverables:
  - Initialize CostTracker in orchestrator.__init__
  - Track embedding costs
  - Track LLM completion costs
  - Update query log with cost

**Task 2.2: Add Cost to Response**
- Location: Modify `app/api.py`
- Purpose: Return cost in response
- Deliverables:
  - Add `cost_usd` field to response
  - Add `budget_remaining` field
  - Budget enforcement before execution

---

### PHASE 3: Prompt Centralization (Medium Priority)

**Task 3.1: Centralize Prompts**
- Location: Update `app/prompts.py`
- Purpose: Single source of truth for prompts
- Deliverables:
  - IntentPrompt registry
  - RiskPrompt registry
  - EscalationPrompt registry
  - Move all prompts from agents to registry

**Task 3.2: Update Agents to Use Registry**
- Locations: All agent files
- Purpose: Use centralized prompts
- Deliverables:
  - Update all agent imports
  - Use registry lookups
  - Remove hardcoded prompts

---

### PHASE 4: Conversation Memory (Medium Priority)

**Task 4.1: Create Memory Manager**
- Location: `app/core/memory.py`
- Purpose: Manage conversation context
- Deliverables:
  - ConversationMemory class
  - Store/retrieve context
  - Summarize old messages
  - Implement sliding window

**Task 4.2: Integrate Memory into Orchestrator**
- Location: Modify `app/orchestrator.py`
- Purpose: Use memory in queries
- Deliverables:
  - Initialize memory per conversation
  - Pass context to agents
  - Update memory after response
  - Handle multi-turn properly

---

### PHASE 5: Trace Emission (Low Priority)

**Task 5.1: Emit Traces in Orchestrator**
- Location: Modify `app/orchestrator.py`
- Purpose: Actually log traces
- Deliverables:
  - Create trace objects
  - Log agent decisions
  - Log risk assessments
  - Log escalations

**Task 5.2: Optional: Langfuse Integration**
- Location: `app/observability/langfuse.py`
- Purpose: Send traces to Langfuse (optional)
- Deliverables:
  - Langfuse client init
  - Send traced events
  - Handle failures gracefully

---

## ✅ Verification Checklist

### Before Demo

**Authentication & Security**
- [ ] Auth middleware active on `/ask`
- [ ] JWT tokens validated
- [ ] Guardrails prevent unsafe queries
- [ ] Test with invalid token → 401

**Cost Tracking**
- [ ] Costs calculated per query
- [ ] Budget enforced
- [ ] Cost returned in response
- [ ] Test budget exceeded → 429

**Prompts**
- [ ] All prompts in app/prompts.py
- [ ] Agents use registry
- [ ] No hardcoded prompts remain

**Conversation Memory**
- [ ] Multi-turn context preserved
- [ ] Memory cleared between sessions
- [ ] Old messages summarized
- [ ] Test 5-turn conversation

**Tracing**
- [ ] Traces logged to DB
- [ ] Agent decisions traced
- [ ] Risk assessments logged
- [ ] Escalations recorded

**API**
- [ ] `GET /health` → 200
- [ ] `POST /ask` with auth → response
- [ ] Cost in response
- [ ] Budget info in response

**Frontend**
- [ ] Connects to backend without errors
- [ ] Can submit query
- [ ] Receives response with cost
- [ ] Multi-turn works

---

## 🚀 Implementation Order

**DAY 1 (Today):**
1. Phase 1: Auth (Critical - 4h)
2. Phase 2: Cost Tracking (2h)
3. Phase 3: Prompts (1.5h)

**DAY 2:**
4. Phase 4: Memory (3h)
5. Phase 5: Traces (1.5h)
6. Testing & verification (3h)

**Total Estimated Effort:** ~15 hours

---

## 📝 Files to Create/Modify

### NEW FILES
- `app/core/auth.py` - Authentication
- `app/core/guardrails.py` - Safety checks
- `app/core/memory.py` - Conversation memory

### MODIFY FILES
- `app/main.py` - Add auth middleware
- `app/api.py` - Add cost tracking, auth checks
- `app/orchestrator.py` - Wire cost, memory, traces
- `app/prompts.py` - Centralize all prompts
- All agent files - Use prompt registry
- `app/observability/langfuse.py` - Langfuse integration

---

## 🎯 Demo Success Criteria

By end of completion:

✅ **Security**: Auth required for `/ask`  
✅ **Cost**: Cost tracked and returned  
✅ **Prompts**: Centralized, maintainable  
✅ **Memory**: Multi-turn conversations work  
✅ **Observability**: Traces emitted  
✅ **Backend**: Fully functional  
✅ **Frontend**: Fully functional  
✅ **Integration**: Both work together  

---

## ⚠️ Demo Day Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can authenticate and get token
- [ ] Can submit policy query
- [ ] Response includes: answer, cost, confidence, risk
- [ ] Multi-turn conversation works
- [ ] Escalation works for high-risk queries
- [ ] Database logs all interactions
- [ ] API documentation accurate
- [ ] No console errors

---

**Status:** Ready to implement  
**Next Step:** Begin Phase 1 (Auth & Security)

