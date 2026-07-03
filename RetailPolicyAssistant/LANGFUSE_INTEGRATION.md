# Langfuse Observability Integration

## Overview

Langfuse is fully integrated into the Retail Policy Intelligence System to provide comprehensive observability, tracing, and monitoring capabilities for all LLM interactions and system operations.

## What's Tracked

### 1. **Request-Level Traces**
Every API request to `/ask` creates a trace that includes:
- User ID and conversation/session ID
- Request metadata (query length, user role)
- Full request lifecycle from validation to response

### 2. **Detailed Spans**
Each trace contains multiple spans for:
- **Permission Check**: User role validation
- **Input Validation**: Query safety and format checking
- **Rate Limit Check**: Token bucket verification
- **Query Orchestration**: Intent detection and routing
- **Cost Tracking**: Token usage and financial impact
- **Error Handling**: Exception tracking and debugging

### 3. **LLM Calls**
Logged for every model invocation:
- Model name and prompt/completion
- Token usage (prompt, completion, total)
- API cost calculation
- Latency metrics
- Model performance tracking

### 4. **RAG Pipeline**
Document retrieval operations tracked:
- Query string
- Retrieved documents (top 3)
- Relevance scores
- Retrieval latency
- Cache hits/misses

### 5. **Risk Assessment**
All security and compliance checks logged:
- Risk level determination
- Risk factors identified
- Escalation decisions
- Compliance flags

### 6. **Guardrail Validation**
Input safety checking tracked:
- PII detection (emails, SSNs, credit cards)
- Injection attack detection
- Safety violations identified
- Risk scores

### 7. **Rate Limiting**
Detailed rate limit decision logging:
- User and endpoint limits
- Tokens remaining
- Request allowance
- Limit breach details

### 8. **Cost Tracking**
Financial metrics captured:
- Query cost (USD)
- Budget remaining
- Budget percentage used
- Token breakdown

## Configuration

### Environment Variables
```bash
LANGFUSE_SECRET_KEY="sk-lf-98777d4a-3a35-4a95-8741-faec16d54cad"
LANGFUSE_PUBLIC_KEY="pk-lf-11158563-967b-4581-acfa-e4244cf175fd"
LANGFUSE_HOST="https://cloud.langfuse.com"
```

These are already set in your `.env` file in `RetailPolicyAssistant/.env`.

## Usage Examples

### Basic Trace Creation
```python
from app.observability.langfuse_tracer import get_tracer

tracer = get_tracer()

# Create a trace
trace = tracer.create_trace(
    name="my-operation",
    user_id="user123",
    session_id="session456",
    metadata={"custom_field": "value"}
)

# Create spans within the trace
tracer.create_span(
    trace,
    name="processing",
    input_data={"query": "What is the refund policy?"},
    output_data={"result": "..."},
)

# Flush to send to Langfuse
tracer.flush()
```

### Logging LLM Calls
```python
tracer.log_llm_call(
    trace,
    model="gpt-4",
    prompt="Answer this question: ...",
    completion="The answer is ...",
    tokens_used={
        "prompt_tokens": 150,
        "completion_tokens": 200,
        "total_tokens": 350,
    },
    cost_usd=0.015,
    latency_ms=850,
)
```

### Logging RAG Operations
```python
tracer.log_rag_retrieval(
    trace,
    query="refund policy",
    documents_retrieved=[
        "Document 1 content...",
        "Document 2 content...",
    ],
    scores=[0.95, 0.87],
    latency_ms=120,
)
```

### Logging Risk Assessment
```python
tracer.log_risk_assessment(
    trace,
    query="What is the refund policy?",
    risk_level="low",
    risk_factors=["non-sensitive-query"],
    escalation_required=False,
)
```

### Logging Guardrail Checks
```python
tracer.log_guardrail_check(
    trace,
    query="What is the refund policy?",
    is_safe=True,
    violations=[],
    risk_score=0.05,
)
```

### Logging Cost Information
```python
tracer.log_cost(
    trace,
    cost_usd=0.015,
    budget_remaining=99.985,
    budget_used_percent=0.015,
    tokens={
        "prompt_tokens": 150,
        "completion_tokens": 200,
    },
)
```

## API Endpoint Tracing

The `/ask` endpoint automatically creates comprehensive traces that include:

1. **Permission validation** - Checks user role and permissions
2. **Input validation** - Validates query format and safety
3. **Rate limit checking** - Verifies rate limit compliance
4. **Query orchestration** - Logs routing and intent detection
5. **Cost calculation** - Tracks financial metrics
6. **Conversation memory** - Stores interaction history
7. **Error handling** - Captures any failures

## Middleware Tracing

The HTTP middleware in `app/main.py` automatically:
- Traces every incoming HTTP request
- Records method, path, and client info
- Captures response status and latency
- Adds trace ID to response headers

## Dashboard & Analytics

### LangfuseDashboard
Access observability metrics through the dashboard module:

```python
from app.observability.langfuse_dashboard import get_dashboard

dashboard = get_dashboard()

# Record metrics after each query
dashboard.record_query_metrics(
    query="What is the refund policy?",
    intent="policy",
    route="rag",
    risk_level="low",
    cost_usd=0.015,
    latency_seconds=0.5,
    user_id="user123",
)

# Get summary metrics
summary = dashboard.get_summary_metrics()
print(f"Total queries: {summary['total_queries']}")
print(f"Success rate: {summary['success_rate']}%")
print(f"Average latency: {summary['average_latency_ms']}ms")

# Get routing distribution
routes = dashboard.get_route_distribution()

# Get full report
report = dashboard.get_full_report()

# Print formatted report
dashboard.print_report()

# Export as JSON
dashboard.export_json("observability_report.json")
```

## Viewing Traces in Langfuse

1. Go to https://cloud.langfuse.com
2. Log in with your account
3. Navigate to your project
4. View real-time traces as queries are processed
5. Analyze performance metrics, costs, and latency
6. Set up alerts and dashboards

## Langfuse Features Used

### Traces
- Container for a complete operation (e.g., one API request)
- Links all related spans and generations
- Includes metadata for filtering and analysis

### Spans
- Represent discrete operations within a trace
- Hierarchical structure for complex workflows
- Include input/output and timing information

### Generations
- Specifically for LLM calls
- Track tokens, cost, and model selection
- Compare different models and prompts

### Observability
- Real-time trace viewing
- Performance analytics
- Cost tracking and budgeting
- Error analysis and debugging

## Performance Considerations

- Traces are flushed automatically at the end of requests
- Langfuse client uses batching for efficiency
- Optional: Disable tracing by removing env variables
- No performance overhead when disabled

## Debugging Tips

1. **Check trace IDs** - Response includes `X-Trace-ID` header
2. **Filter by user** - Use user_id in Langfuse interface
3. **View span details** - Expand spans to see full input/output
4. **Check latencies** - Identify slow operations
5. **Monitor costs** - Track budget usage in real-time

## Integration Points

- ✅ API request middleware
- ✅ Permission checking
- ✅ Input validation
- ✅ Rate limiting
- ✅ Query orchestration
- ✅ LLM calls
- ✅ RAG operations
- ✅ Risk assessment
- ✅ Cost tracking
- ✅ Error handling
- ✅ Conversation memory

## Next Steps

1. **Deploy to production** - Traces will be sent to Langfuse
2. **Set up alerts** - Monitor for errors or cost overages
3. **Create dashboards** - Custom metrics and analytics
4. **Integrate with monitoring** - Connect with PagerDuty, Slack
5. **Analyze patterns** - Find optimization opportunities

## Support

For questions about Langfuse:
- 📚 Documentation: https://langfuse.com/docs
- 💬 Community: https://discord.gg/mHrZsqBp
- 🐛 Issues: https://github.com/langfuse/langfuse

For questions about this integration:
- Check existing spans in Langfuse UI
- Review trace IDs from response headers
- Examine code in `app/observability/langfuse_tracer.py`
