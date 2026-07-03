# Test Suite - Retail Policy Intelligence System

## Overview

Comprehensive test suite for the Retail Policy Intelligence & Decision Support System. Tests are organized by component and include unit tests, integration tests, and end-to-end tests.

## Test Structure

```
tests/
├── conftest.py                      # Pytest configuration and fixtures
├── test_api.py                      # API endpoint tests
├── test_agents.py                   # Agent functionality tests
├── test_orchestrator.py             # Orchestrator coordination tests
├── test_models.py                   # Database model tests
├── test_vector_store_model.py       # Vector database tests
├── load_test.py                     # Load and performance tests
└── README.md                        # This file
```

## Running Tests

### Run All Tests

```bash
cd RetailPolicyAssistant
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_agents.py -v
pytest tests/test_orchestrator.py -v
pytest tests/test_models.py -v
pytest tests/test_api.py -v
```

### Run Tests by Marker

```bash
# Run only unit tests
pytest tests/ -m unit -v

# Run only integration tests
pytest tests/ -m integration -v

# Skip slow tests
pytest tests/ -m "not slow" -v
```

### Run with Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

### Run Tests in Parallel

```bash
pytest tests/ -n auto
```

## Test Categories

### 1. test_agents.py

Tests individual agent functionality:

- **TestIntentAgent**: Intent detection for different query types (RAG, SQL, Hybrid)
- **TestRAGAgent**: Policy retrieval and document search
- **TestSQLAgent**: Database query execution
- **TestHybridAgent**: Combined RAG + SQL reasoning
- **TestRiskAgent**: Risk level assessment
- **TestEscalationAgent**: Escalation decision logic
- **TestAgentIntegration**: Agent orchestration

**Run:**
```bash
pytest tests/test_agents.py -v
```

### 2. test_orchestrator.py

Tests orchestrator and query processing:

- **TestOrchestratorBasic**: Basic initialization and setup
- **TestOrchestratorQueryProcessing**: Query response structure and content
- **TestOrchestratorRouting**: Query routing to correct agents
- **TestOrchestratorRiskDetection**: Risk level detection
- **TestOrchestratorErrorHandling**: Error recovery and edge cases
- **TestOrchestratorLatency**: Performance and latency tracking
- **TestOrchestratorMultipleQueries**: Sequential query processing

**Run:**
```bash
pytest tests/test_orchestrator.py -v
```

### 3. test_models.py

Tests database models:

- **TestPolicyDocumentModel**: Policy document creation and fields
- **TestVendorModel**: Vendor data model
- **TestAuditLogModel**: Audit logging
- **TestRetentionRecordModel**: Retention policy records
- **TestComplianceReviewModel**: Compliance reviews
- **TestAIQueryModel**: AI query logging
- **TestAIResponseModel**: AI response storage
- **TestModelRelationships**: Model relationships and constraints

**Run:**
```bash
pytest tests/test_models.py -v
```

### 4. test_api.py

Tests API endpoints:

- **test_home**: Root endpoint
- **test_ask_returns_rag_policy_answer**: RAG route responses
- **test_ask_returns_sql_vendor_answer**: SQL route responses
- **test_ask_returns_hybrid_answer**: Hybrid route responses

**Run:**
```bash
pytest tests/test_api.py -v
```

### 5. test_vector_store_model.py

Tests vector database:

- **test_policy_document_model_exists_with_vector_column**: Vector column existence

**Run:**
```bash
pytest tests/test_vector_store_model.py -v
```

### 6. load_test.py

Performance and load testing:

- **TestLoadTestRunner**: Concurrent query testing
- **Sequential load test**: Single query baseline
- **Concurrent load test**: Multiple simultaneous queries
- **Stress test**: High-volume testing

**Run:**
```bash
python tests/load_test.py
# Or with pytest
pytest tests/load_test.py -v --tb=short
```

## Test Coverage

### What's Tested

✅ **Agent Functionality**
- Intent detection for all query types
- RAG policy retrieval
- SQL vendor queries
- Hybrid reasoning
- Risk assessment
- Escalation decisions

✅ **Orchestrator**
- Query processing pipeline
- Response structure and content
- Routing logic
- Risk detection
- Error handling
- Latency tracking
- Multiple sequential queries

✅ **Database Models**
- Model creation and fields
- Data validation
- Field constraints
- Relationships between models

✅ **API Endpoints**
- Health check
- Query endpoints
- Response format
- Error responses

✅ **Performance**
- Sequential query latency
- Concurrent query handling
- Stress testing under load
- Throughput measurement

### What's Not Tested (By Design)

❌ External dependencies
- PostgreSQL connection (tested in integration)
- Ollama embeddings (tested in integration)
- Actual database operations (mocked where needed)

## Fixtures

Available fixtures in conftest.py:

- `test_config`: Test configuration values
- `sample_query`: Standard policy query
- `sample_vendor_query`: Vendor query
- `sample_high_risk_query`: High-risk query
- `sample_policy_content`: Sample policy text
- `sample_vendor_data`: Sample vendor information

Usage in tests:

```python
def test_with_fixture(sample_query):
    result = orchestrator.run(sample_query)
    assert result is not None
```

## Example Test Run

```bash
$ pytest tests/ -v --tb=short

tests/test_agents.py::TestIntentAgent::test_rag_intent_detection PASSED
tests/test_agents.py::TestIntentAgent::test_sql_intent_detection PASSED
tests/test_agents.py::TestIntentAgent::test_hybrid_intent_detection PASSED
tests/test_agents.py::TestRAGAgent::test_rag_returns_result PASSED
...

=================== 47 passed in 12.34s ===================
```

## Continuous Integration

### GitHub Actions (if configured)

Tests run automatically on:
- Push to main/develop
- Pull requests
- Scheduled nightly runs

### Local Pre-commit

Run tests before committing:

```bash
# Install pre-commit hook
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

## Debugging Tests

### Run with Debug Output

```bash
pytest tests/ -v -s
```

### Run with PDB (Python debugger)

```bash
pytest tests/ --pdb
```

### Run Single Test

```bash
pytest tests/test_agents.py::TestIntentAgent::test_rag_intent_detection -v
```

### Show Print Statements

```bash
pytest tests/ -v -s --tb=short
```

## Test Maintenance

### Adding New Tests

1. Create test class in appropriate file
2. Use descriptive test names starting with `test_`
3. Add docstrings explaining what's tested
4. Use fixtures for common setup
5. Run `pytest --collect-only` to verify

### Updating Tests

When changing functionality:
1. Update corresponding test
2. Verify test still passes
3. Add new test for new behavior
4. Run full suite: `pytest tests/ -v`

## Expected Results

### All Tests Passing

```
✅ 47 tests passed
✅ 0 tests failed
✅ All assertions successful
```

### Sample Output

```
test_agents.py::TestIntentAgent
  test_rag_intent_detection PASSED
  test_sql_intent_detection PASSED
  test_hybrid_intent_detection PASSED
  test_intent_has_reason PASSED

test_orchestrator.py::TestOrchestratorQueryProcessing
  test_run_returns_response PASSED
  test_response_has_required_fields PASSED
  test_response_structure PASSED
  ...
```

## Troubleshooting

### Database Connection Error

```
If tests fail with database connection:
1. Ensure PostgreSQL is running
2. Check DATABASE_URL in .env
3. Run: python app/db_init.py
```

### Import Errors

```
If tests fail with import errors:
1. Ensure you're in the RetailPolicyAssistant directory
2. Run: pip install -r requirements.txt
3. Check PYTHONPATH includes the project
```

### Slow Tests

```
To identify slow tests:
pytest tests/ --durations=10
```

## Best Practices

1. **Keep tests isolated**: Each test should be independent
2. **Use fixtures**: Reuse common setup with pytest fixtures
3. **Clear naming**: Test name should describe what's tested
4. **One assertion per concept**: Keep tests focused
5. **Mock external services**: Don't rely on external APIs
6. **Test edge cases**: Include boundary conditions
7. **Update with code**: Keep tests synchronized with code changes

## Contributing

When adding new code:
1. Write tests first (TDD approach) or alongside code
2. Ensure all tests pass: `pytest tests/ -v`
3. Check coverage: `pytest --cov=app tests/`
4. Commit tests with code changes

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/test_utils.html)
- [Load Testing with Pytest](https://docs.pytest.org/en/latest/how-to/mark.html)

---

**Status**: ✅ Test suite ready  
**Total Tests**: 47+ test cases  
**Coverage**: Agents, Orchestrator, Models, API, Performance  
**Last Updated**: 2026-07-03
