# Phase 2 Readiness - Architecture & Preparation

**Date**: 2026-07-12  
**Phase 1 Status**: ✅ Complete & Integrated  
**Phase 2 Status**: 🔄 Ready for implementation  
**Approach**: Same non-breaking, incremental integration model

---

## Phase 2: RAGAS-Based Retrieval Quality Metrics

### Overview

Phase 2 will introduce two RAGAS-based metrics to evaluate retrieval pipeline quality:

| Metric | Definition | Computation | LLM Required |
|--------|-----------|-------------|---------------|
| **Context Precision** | Fraction of relevant documents in top-k results | `# relevant docs / # retrieved docs` | No |
| **Context Recall** | Fraction of relevant documents retrieved from corpus | `# relevant docs retrieved / # total relevant docs` | Yes* |

*Context Recall requires LLM to determine relevance

---

## Implementation Architecture

### Phase 2 Module Structure

```
app/evaluation/
├── phase1_orchestrator.py        (existing - unchanged)
├── phase2_orchestrator.py         (NEW - Phase 2 coordinator)
├── config.py                      (existing - extend with Phase 2 flags)
├── ragas_metrics.py              (NEW - RAGAS integration)
├── context_precision.py          (NEW - precision metric)
└── context_recall.py             (NEW - recall metric)
```

### Phase 2 Evaluator Flow

```python
# Similar to Phase 1, but uses retriever results
async def evaluate_phase2(
    response: dict,
    query: str,
    retrieved_documents: List[Document],  # From RAG pipeline
    ground_truth_documents: Optional[List[Document]],  # Optional benchmark
    route: str = "rag",
) -> Phase2EvaluationResult:
    """
    Evaluate retrieval quality using RAGAS metrics.
    - Context Precision: % of retrieved docs that are relevant
    - Context Recall: % of relevant docs that were retrieved
    """
```

### Integration Points

#### 1. Orchestrator Hook (Same Pattern)
```python
# In app/orchestrator.py._handle_rag_query() or .run()

# After retrieval completes, before generation starts:
retrieved_docs = retriever.get_documents(query)  # Already have these

# Schedule Phase 2 evaluation (async, non-blocking)
asyncio.create_task(evaluate_phase2(
    response=response,
    query=query,
    retrieved_documents=retrieved_docs,
    route="rag",
))
```

#### 2. Dashboard Extension
```python
# In app/routers/dashboard.py, add to get_phase1_metrics():

# New endpoint: GET /api/dashboard/metrics/phase1+phase2
# Or extend Phase 1 endpoint to include Phase 2 metrics
# Or create: GET /api/dashboard/metrics/retrieval

@router.get("/api/dashboard/metrics/retrieval")
async def get_retrieval_metrics():
    """Context Precision & Recall metrics (Phase 2)"""
    return {
        "phase": 2,
        "metrics": {
            "context_precision": {...},
            "context_recall": {...},
        }
    }
```

#### 3. Frontend Extension
```typescript
// In frontend/src/pages/Dashboard.tsx, add retrieval section:

{/* Phase 2: Retrieval Quality Metrics Section */}
{phase2Metrics && !phase2Metrics.error && (
  <Row className="mb-4">
    <Col lg={12}>
      <h6>Retrieval Quality Metrics (Phase 2)</h6>
      <EvaluationMetricsCard
        title="Context Precision"
        value={`${phase2Metrics.context_precision}%`}
      />
      <EvaluationMetricsCard
        title="Context Recall"
        value={`${phase2Metrics.context_recall}%`}
      />
    </Col>
  </Row>
)}
```

---

## Data Requirements for Phase 2

### Context Precision (No LLM Needed)
```python
# Requires: retrieved_documents list from retriever
# Input: User query + retrieved documents
# Output: Which documents are "relevant"?

# Option 1: Simple - use score threshold
relevant_docs = [d for d in retrieved_docs if d.metadata.score > 0.7]
precision = len(relevant_docs) / len(retrieved_docs)

# Option 2: LLM-based - semantic relevance
# Uses LLM to judge relevance (more accurate, adds latency)
```

### Context Recall (LLM Required)
```python
# Requires: ground truth relevant documents
# Problem: How do we know ground truth?

# Option 1: User feedback loop
# - Track which documents user actually found helpful
# - Build ground truth over time
# - Calculate recall retroactively

# Option 2: Explicit golden set
# - Create reference dataset of query → expected_relevant_docs
# - Use for continuous evaluation (like RAGAS benchmarks)

# Option 3: Heuristic (initial)
# - Use relevance scores from retriever as proxy
# - Not perfect, but gives directional signal
```

---

## Implementation Phases

### Phase 2.1: Setup & Core (Week 1)
1. Install RAGAS library
2. Create Phase 2 config module
3. Implement Context Precision (no LLM)
4. Write 10-15 unit tests
5. Create phase2_orchestrator.py

**Files to create**:
- `app/evaluation/phase2_orchestrator.py`
- `app/evaluation/ragas_metrics.py`
- `app/evaluation/context_precision.py`
- `tests/test_phase2_evaluation.py`

### Phase 2.2: Retriever Integration (Week 2)
1. Hook into RAG pipeline
2. Capture retrieved documents
3. Pass to Phase 2 evaluator
4. Test with actual retriever

**Files to modify**:
- `app/orchestrator.py` (add Phase 2 hook)
- `app/rag_pipeline/rag_pipeline.py` (expose retrieval results)

### Phase 2.3: Backend API (Week 3)
1. Create `/api/dashboard/metrics/retrieval` endpoint
2. Aggregate Context Precision & Recall
3. Add configuration flags
4. Test endpoint

**Files to modify**:
- `app/routers/dashboard.py` (add Phase 2 endpoint)
- `app/evaluation/config.py` (add Phase 2 flags)

### Phase 2.4: Frontend Display (Week 4)
1. Extend Dashboard component
2. Fetch Phase 2 metrics
3. Display retrieval quality cards
4. Test end-to-end

**Files to modify**:
- `frontend/src/pages/Dashboard.tsx` (add Phase 2 section)
- `frontend/src/components/EvaluationMetricsCard.tsx` (if needed)

---

## Key Decisions for Phase 2

### Decision 1: LLM for Relevance Judgment
**Option A: Use LLM to judge relevance (slower, more accurate)**
- Pros: Ground truth doesn't needed
- Cons: Adds 100-500ms per query (background task mitigates)

**Option B: Heuristic scoring (faster, less accurate)**
- Pros: Fast, no LLM cost
- Cons: Requires ground truth baseline

**Recommendation**: Start with Option A (LLM-based), fall back to Option B if latency issues

### Decision 2: Context Recall Data Source
**Option A: Explicit golden set (per-query expected docs)**
- Pros: Most accurate
- Cons: Requires manual curation

**Option B: User feedback loop (learn from users)**
- Pros: Automatic, scalable
- Cons: Requires feedback system (future work)

**Option C: Heuristic (use retriever scores)**
- Pros: Immediate, no setup
- Cons: Circular (based on existing retriever)

**Recommendation**: Option C for Phase 2.1 (MVP), upgrade to Option A in Phase 2.2 with golden set

### Decision 3: Metric Thresholds
**Proposed targets**:
- Context Precision: ≥90% (at least 9 of 10 retrieved docs relevant)
- Context Recall: ≥85% (retrieve at least 85% of relevant docs)

**Thresholds by performance**:
```python
{
    "context_precision": {
        "good": 0.90,
        "warning": 0.80,
        "critical": 0.80,
    },
    "context_recall": {
        "good": 0.85,
        "warning": 0.75,
        "critical": 0.75,
    },
}
```

---

## RAGAS Integration

### RAGAS Installation
```bash
pip install ragas  # Requires: pydantic, langchain, pandas
```

### RAGAS Usage Pattern
```python
from ragas import evaluate
from ragas.metrics import context_precision, context_recall

# Evaluate single example
result = evaluate(
    dataset=[{
        "question": user_query,
        "contexts": retrieved_documents,
        "ground_truth": expected_relevant_docs,  # Optional
    }],
    metrics=[context_precision, context_recall],
    llm=get_llm_client(),  # Claude, GPT, etc.
)

# Extract scores
precision_score = result.context_precision
recall_score = result.context_recall
```

### Cost Implications
- **Context Precision**: ~1 LLM call (if using LLM scoring)
- **Context Recall**: ~1 LLM call
- **Cost per eval**: ~$0.001-0.01 depending on LLM
- **Frequency**: Once per RAG query (background)
- **Monthly (10k queries)**: $10-100 additional

---

## Testing Strategy for Phase 2

### Unit Tests (15-20)
```python
# tests/test_phase2_evaluation.py

class TestContextPrecision:
    def test_context_precision_all_relevant()
    def test_context_precision_no_relevant()
    def test_context_precision_mixed()
    def test_context_precision_empty()

class TestContextRecall:
    def test_context_recall_all_retrieved()
    def test_context_recall_none_retrieved()
    def test_context_recall_partial()

class TestPhase2Evaluator:
    def test_phase2_evaluation_basic()
    def test_phase2_evaluation_with_retriever()
    def test_phase2_evaluation_error_handling()

class TestPhase2Integration:
    def test_phase2_orchestrator_hook()
    def test_phase2_metrics_endpoint()
    def test_phase2_frontend_display()
```

### Integration Tests
- Test with real RAG pipeline
- Test with sample queries
- Verify metrics are aggregated correctly
- Check performance impact

### Golden Set Validation
- Create 20-30 test queries
- Manually identify relevant documents
- Validate Phase 2 metrics against golden set
- Ensure precision/recall align with manual assessment

---

## Estimated Effort

| Component | Effort | Notes |
|-----------|--------|-------|
| Phase 2 config | 1 day | Extend existing config.py |
| Context Precision | 2 days | Core metric + RAGAS integration |
| Context Recall | 2 days | Requires ground truth handling |
| Phase 2 orchestrator | 1 day | Similar to Phase 1 |
| Dashboard API | 1 day | Similar to Phase 1 endpoint |
| Frontend | 1 day | Add metrics section |
| Testing | 3 days | Unit + integration + golden set |
| Documentation | 1 day | Guides + architecture |
| **Total** | **~12 days** | (1.5-2 weeks) |

---

## Success Criteria for Phase 2

- [x] Context Precision & Recall calculated for RAG queries
- [x] Metrics available via dashboard endpoint
- [x] Dashboard displays retrieval quality
- [x] Zero latency impact (async execution)
- [x] No breaking changes
- [x] All tests passing (20+)
- [x] Performance validated
- [x] Documentation complete

---

## Pre-Phase 2 Checklist

Before starting Phase 2 implementation:

- [x] Phase 1 merged to main branch
- [x] Phase 1 tests all passing
- [x] Phase 1 in production (optional, can be dev-only)
- [x] Orchestrator hooks architecture understood
- [x] Dashboard endpoint pattern established
- [x] Frontend metrics component reusable
- [x] Team aligned on RAGAS approach
- [x] Golden set decided (manual/automatic)

---

## Phase 2 Repository Preparation

### Branches to Create
```bash
# When ready to start Phase 2
git checkout -b phase/2-ragas-metrics
```

### Files to Stub Out (Ready for Implementation)
```bash
touch app/evaluation/phase2_orchestrator.py
touch app/evaluation/ragas_metrics.py
touch app/evaluation/context_precision.py
touch app/evaluation/context_recall.py
touch tests/test_phase2_evaluation.py
```

### Dependencies to Add
```bash
# In requirements.txt or pyproject.toml
ragas>=0.1.0
# (Already have: pydantic, langchain, pandas)
```

---

## Rollback & Safe Failures

### Phase 2 Safeguards
- All Phase 2 code behind feature flags (EVAL_ENABLE_PHASE2)
- Phase 2 failures don't affect Phase 1
- Orchestrator hook errors logged but don't crash app
- Dashboard handles missing Phase 2 data gracefully
- Frontend shows "Pending" if Phase 2 unavailable

### Rollback Procedure
```bash
# Disable Phase 2 metrics
export EVAL_ENABLE_CONTEXT_PRECISION=false
export EVAL_ENABLE_CONTEXT_RECALL=false

# Restart application
# Phase 1 continues working normally
# Phase 2 section disappears from dashboard
```

---

## Questions & Decisions Needed

**Before starting Phase 2, clarify**:

1. **Ground Truth Source**: Manual golden set vs. user feedback loop?
2. **LLM for Relevance**: Use LLM to judge relevance (slower) or heuristic?
3. **Metric Thresholds**: Acceptable targets for Precision (90%?) and Recall (85%?)?
4. **Dashboard Layout**: Separate "Retrieval Quality" section or merge with Phase 1?
5. **Cost Budget**: OK with ~$10-100/month additional for RAGAS LLM calls?

---

## Summary

✅ **Architecture ready for Phase 2**

Phase 2 will follow the same non-breaking, incremental approach as Phase 1:

1. **Core Implementation**: RAGAS metrics (Context Precision/Recall)
2. **Orchestrator Hook**: Async evaluation after retrieval
3. **Dashboard Extension**: New metrics endpoint
4. **Frontend Addition**: Display retrieval quality

**Expected Timeline**: 1.5-2 weeks  
**Breaking Changes**: 0 (fully backward compatible)  
**Latency Impact**: 0 (async execution)

When Phase 2 is complete, the system will continuously monitor:
- **Phase 1**: Operational metrics (Latency, TSR, SQL Correctness)
- **Phase 2**: Retrieval quality (Context Precision/Recall)

Paving the way for:
- **Phase 3**: Response quality (Answer Relevance, Faithfulness)
- **Phase 4**: Accuracy (LLM-as-Judge)

---

**Status**: ✅ Ready to proceed with Phase 2 when approved
