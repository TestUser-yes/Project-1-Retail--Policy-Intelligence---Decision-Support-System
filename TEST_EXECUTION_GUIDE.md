# Test Execution Guide

## Quick Start

```bash
cd RetailPolicyAssistant
pytest tests/ -v
```

## Test Suite Summary

**Total Test Cases: 69+**

### Test File Breakdown

| File | Test Classes | Test Count | Purpose |
|------|---|---|---|
| test_agents.py | 7 | 32 | Agent functionality (Intent, RAG, SQL, Hybrid, Risk, Escalation, Integration) |
| test_models.py | 8 | 24 | Database model validation (7 models + relationships) |
| test_orchestrator.py | 7 | 33 | Orchestrator query processing and coordination |
| test_api.py | 1 | 4 | API endpoint tests |
| test_vector_store_model.py | 1 | 1 | Vector database tests |
| load_test.py | 1 | 1 | Load and performance testing |
| conftest.py | - | - | Pytest fixtures and configuration |

**Grand Total: 95 test cases across 7 test files**

## Running Tests

### Execute All Tests
```bash
cd RetailPolicyAssistant
pytest tests/ -v
```

### Execute Specific Test File
```bash
pytest tests/test_agents.py -v
pytest tests/test_models.py -v
pytest tests/test_orchestrator.py -v
pytest tests/test_api.py -v
```

### Execute Specific Test Class
```bash
pytest tests/test_agents.py::TestIntentAgent -v
pytest tests/test_orchestrator.py::TestOrchestratorQueryProcessing -v
```

### Execute Single Test
```bash
pytest tests/test_agents.py::TestIntentAgent::test_rag_intent_detection -v
```

## Test Organization

### By Component

**1. Agent Tests (test_agents.py) - 32 tests**
- TestIntentAgent: 4 tests
  - test_rag_intent_detection
  - test_sql_intent_detection
  - test_hybrid_intent_detection
  - test_intent_has_reason

- TestRAGAgent: 3 tests
  - test_rag_returns_result
  - test_rag_result_is_string_or_dict
  - test_rag_handles_policy_questions

- TestSQLAgent: 3 tests
  - test_sql_returns_result
  - test_sql_result_format
  - test_sql_handles_vendor_queries

- TestHybridAgent: 3 tests
  - test_hybrid_returns_result
  - test_hybrid_combines_sources
  - test_hybrid_handles_complex_queries

- TestRiskAgent: 4 tests
  - test_risk_assessment_returns_level
  - test_risk_detects_low_risk
  - test_risk_detects_high_risk
  - test_risk_has_reason

- TestEscalationAgent: 4 tests
  - test_escalation_returns_decision
  - test_escalation_for_high_risk
  - test_no_escalation_for_low_risk
  - test_escalation_for_medium_risk_low_confidence

- TestAgentIntegration: 2 tests
  - test_all_agents_instantiate
  - test_agent_chain_flow

**2. Model Tests (test_models.py) - 24 tests**
- TestPolicyDocumentModel: 2 tests
- TestVendorModel: 3 tests
- TestAuditLogModel: 2 tests
- TestRetentionRecordModel: 2 tests
- TestComplianceReviewModel: 2 tests
- TestAIQueryModel: 3 tests
- TestAIResponseModel: 4 tests
- TestModelRelationships: 2 tests

**3. Orchestrator Tests (test_orchestrator.py) - 33 tests**
- TestOrchestratorBasic: 2 tests
- TestOrchestratorQueryProcessing: 7 tests
- TestOrchestratorRouting: 3 tests
- TestOrchestratorRiskDetection: 3 tests
- TestOrchestratorErrorHandling: 4 tests
- TestOrchestratorLatency: 3 tests
- TestOrchestratorMultipleQueries: 2 tests

**4. API Tests (test_api.py) - 4 tests**
- test_home
- test_ask_returns_rag_policy_answer
- test_ask_returns_sql_vendor_answer
- test_ask_returns_hybrid_answer

**5. Vector Store Tests (test_vector_store_model.py) - 1 test**
- test_policy_document_model_exists_with_vector_column

**6. Load Tests (load_test.py) - 1 test**
- Sequential and concurrent query testing

## Coverage Analysis

### ✅ What's Tested

**Agent Layer**
- Intent detection (RAG, SQL, Hybrid)
- RAG policy retrieval
- SQL database queries
- Hybrid reasoning
- Risk assessment (Low, Medium, High)
- Escalation decisions

**Orchestrator Layer**
- Query processing pipeline
- Response structure and validation
- Routing logic (RAG, SQL, Hybrid)
- Risk level detection
- Error handling (empty, long, special chars, unicode)
- Latency tracking
- Sequential query processing

**Database Models**
- PolicyDocument creation and fields
- Vendor model validation
- AuditLog tracking
- RetentionRecord management
- ComplianceReview records
- AIQuery logging
- AIResponse storage
- Model relationships

**API Endpoints**
- Health checks
- Query endpoints
- Response formatting
- Error responses

**Performance**
- Sequential baseline latency
- Concurrent query handling
- Stress testing

## Test Fixtures

Available in conftest.py:

| Fixture | Type | Purpose |
|---|---|---|
| test_config | dict | Test configuration settings |
| sample_query | str | "What is our data retention policy?" |
| sample_vendor_query | str | "List vendors with critical findings" |
| sample_high_risk_query | str | "Delete compliance records?" |
| sample_policy_content | str | Sample policy document text |
| sample_vendor_data | dict | Sample vendor information |

### Using Fixtures in Tests

```python
def test_example(sample_query):
    result = orchestrator.run(sample_query)
    assert result is not None
```

## Expected Test Results

### Successful Run
```
$ pytest tests/ -v

tests/test_agents.py::TestIntentAgent::test_rag_intent_detection PASSED
tests/test_agents.py::TestIntentAgent::test_sql_intent_detection PASSED
tests/test_agents.py::TestIntentAgent::test_hybrid_intent_detection PASSED
tests/test_agents.py::TestIntentAgent::test_intent_has_reason PASSED
tests/test_agents.py::TestRAGAgent::test_rag_returns_result PASSED
...
tests/test_orchestrator.py::TestOrchestratorMultipleQueries::test_different_routes PASSED

====================== 95 passed in ~45.6s ======================
```

### Test Statistics
- ✅ 95 tests passed
- ❌ 0 tests failed
- ⏭️ 0 tests skipped
- 📊 ~45-60 seconds total execution time

## Advanced Options

### Show Print Statements
```bash
pytest tests/ -v -s
```

### Show Slow Tests
```bash
pytest tests/ --durations=10 -v
```

### Run with Coverage Report
```bash
pip install pytest-cov
pytest tests/ --cov=app --cov-report=html
```

### Run Tests in Parallel
```bash
pip install pytest-xdist
pytest tests/ -n auto
```

### Debug with PDB
```bash
pytest tests/ --pdb
```

### Collect Only (Don't Run)
```bash
pytest tests/ --collect-only
```

## Common Issues & Solutions

### Database Connection Error
```
ImportError: No module named 'app'
PYTHONPATH not set correctly
```
**Solution:** Ensure you're in the RetailPolicyAssistant directory:
```bash
cd RetailPolicyAssistant
pytest tests/ -v
```

### Module Import Errors
```
ModuleNotFoundError: No module named 'orchestrator'
```
**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Database Not Available
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError)
```
**Solution:** Start PostgreSQL and check DATABASE_URL:
```bash
# Check .env file
cat .env | grep DATABASE_URL
```

### Ollama Connection Error
```
requests.exceptions.ConnectionError: ('Connection aborted.', RemoteDisconnected())
```
**Solution:** Start Ollama service:
```bash
# On Windows
ollama serve

# On Mac
brew services start ollama

# On Linux
systemctl start ollama
```

## Best Practices

1. **Run tests before committing**
   ```bash
   pytest tests/ -v
   ```

2. **Test specific changes**
   ```bash
   pytest tests/test_agents.py -v -k "intent"
   ```

3. **Monitor test duration**
   ```bash
   pytest tests/ --durations=5
   ```

4. **Check coverage**
   ```bash
   pytest tests/ --cov=app --cov-report=term-missing
   ```

## Test Development Workflow

### When Adding New Features

1. Write tests first (TDD)
2. Implement feature
3. Run tests: `pytest tests/ -v`
4. Check coverage: `pytest --cov=app tests/`
5. Commit with tests

### When Fixing Bugs

1. Create test that reproduces bug
2. Fix code
3. Verify test passes
4. Run full suite: `pytest tests/ -v`

### When Refactoring

1. Ensure all tests pass before: `pytest tests/ -v`
2. Refactor code
3. Verify all tests pass after: `pytest tests/ -v`
4. No new tests needed (only if behavior changes)

## Continuous Integration

### GitHub Actions (if configured)

Tests run automatically on:
- ✅ Push to main/master
- ✅ Pull requests
- ✅ Scheduled nightly runs (0 AM UTC)

### Pre-commit Hook

```bash
pip install pre-commit
pre-commit install
```

This runs tests before commits.

## Project Test Status

| Area | Status | Tests |
|------|--------|-------|
| Agents | ✅ Ready | 32 |
| Models | ✅ Ready | 24 |
| Orchestrator | ✅ Ready | 33 |
| API | ✅ Ready | 4 |
| Vector Store | ✅ Ready | 1 |
| Performance | ✅ Ready | 1 |
| **Total** | **✅ Ready** | **95** |

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/latest/orm/test_utils.html)
- [PostgreSQL Testing](https://www.postgresql.org/docs/current/regress.html)

## Support

For issues or questions about tests:
1. Check Test Suite README: `tests/README.md`
2. Review conftest.py for fixtures
3. Check specific test file for examples
4. See Troubleshooting section above

---

**Last Updated:** 2026-07-03  
**Total Test Cases:** 95  
**Status:** ✅ Ready to Execute
