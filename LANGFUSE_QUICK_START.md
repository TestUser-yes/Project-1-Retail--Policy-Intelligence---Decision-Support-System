# Langfuse Quick Start Guide

## 🚀 Getting Started in 2 Minutes

### 1. View Your Traces

1. Go to: **https://cloud.langfuse.com**
2. Log in with your account
3. Select your project
4. You'll see real-time traces as queries happen

### 2. Make a Query to Generate Traces

```bash
# Start the backend
cd RetailPolicyAssistant
uvicorn app.main:app --reload

# In another terminal, get a token
curl http://localhost:8000/token

# Use the token to ask a question
curl -X POST http://localhost:8000/ask \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the refund policy?"}'
```

### 3. Watch the Trace Appear in Langfuse

- Response includes `X-Trace-ID` header
- Go to Langfuse and search for that trace ID
- Click to expand and see all spans

---

## 📊 What You'll See in Langfuse

### Trace View
```
┌─ ask-query [conversation_id]
│  ├─ permission-check (2ms)
│  ├─ input-validation (5ms)
│  ├─ rate-limit-check (1ms)
│  ├─ query-orchestration (150ms)
│  │  ├─ intent: policy
│  │  ├─ route: rag
│  │  └─ risk: low
│  ├─ cost-tracking (metadata)
│  └─ http-response (200ms)
```

### Span Details
- **Input**: What went in (query, user ID, etc.)
- **Output**: What came out (result, status, metrics)
- **Metadata**: Custom fields (cost, latency, tokens)
- **Timing**: Exact duration of each operation

---

## 🔍 Common Use Cases

### View All Queries from a User
1. Click **Filters** → **Add filter**
2. Select **metadata → user_id**
3. Enter user ID
4. See all that user's queries with costs and latency

### Find Slow Queries
1. Click **Traces** tab
2. Sort by **Latency** (descending)
3. Identify queries taking >1000ms
4. Click to analyze bottlenecks

### Monitor Costs
1. Click **Dashboard** (if available)
2. Look for cost metrics
3. View budget burn rate
4. Set up cost alerts

### Find Errors
1. Filter by **Status** → **Error**
2. See which operations failed
3. View error messages in span details
4. Check error count over time

### Compare Routes
1. Filter by **metadata → route**
2. Compare RAG vs SQL performance
3. Check cost differences
4. Optimize route selection

---

## 📈 Key Metrics to Monitor

| Metric | Where | Good Range |
|--------|-------|-----------|
| **Avg Latency** | Dashboard | < 500ms |
| **Success Rate** | Dashboard | > 95% |
| **Cost/Query** | Trace details | < $0.02 |
| **Budget Used** | Dashboard | < 80% |
| **Route Distribution** | Filters | Balanced |
| **Risk Level** | Metadata | Mostly Low |

---

## 🛠️ Advanced Usage

### Filter by Multiple Conditions
1. Click **Filters**
2. Add multiple conditions:
   - `metadata.user_id == "user123"`
   - `metadata.route == "rag"`
   - `metadata.risk_level == "high"`
3. View matching traces

### Export Data
1. Select traces
2. Click **Export** (if available)
3. Save as JSON/CSV
4. Analyze in Excel or Python

### Set Up Alerts
1. Go to **Settings** → **Alerts**
2. Create alert for:
   - Error rate > 5%
   - Latency > 2000ms
   - Cost > $10/day
3. Receive notifications

### Create Custom Dashboard
1. Go to **Dashboards**
2. Create new dashboard
3. Add widgets:
   - Query count over time
   - Cost by route
   - Success rate trend
   - Top users

---

## 🔑 Environment Variables

Already configured in `RetailPolicyAssistant/.env`:

```env
LANGFUSE_SECRET_KEY="sk-lf-..."      # Secret key for API access
LANGFUSE_PUBLIC_KEY="pk-lf-..."      # Public key for SDK
LANGFUSE_HOST="https://cloud.langfuse.com"  # Langfuse endpoint
```

No additional setup needed! Traces start automatically.

---

## 💡 Pro Tips

1. **Check Trace IDs**: Every response has `X-Trace-ID` header
   - Copy this ID to quickly find trace in Langfuse

2. **Search by Conversation**: Traces include `session_id` (conversation_id)
   - View full conversation history in one view

3. **Monitor Budget**: Cost metrics in every trace
   - Track daily spending in real-time

4. **Compare Versions**: Different prompts/models show different costs
   - Use traces to optimize

5. **Debug Issues**: View full request/response in spans
   - No guessing - see exactly what happened

---

## ❌ Troubleshooting

### Traces Not Appearing

1. **Check credentials**: Verify `.env` has valid keys
2. **Check network**: Ensure internet connectivity
3. **Check console**: Look for error messages
4. **Check timing**: Give 1-2 seconds for traces to appear

### Traces Appearing but Empty

1. **Check filters**: You might be filtering them out
2. **Check date range**: Ensure today's date selected
3. **Refresh page**: Langfuse UI may need refresh

### Missing Spans

1. **Check for errors**: Errors may prevent some spans
2. **Check rate limiting**: If rate limited, some spans skipped
3. **Check permissions**: Permission denial stops processing

---

## 📚 Documentation

- **Full Guide**: See `RetailPolicyAssistant/LANGFUSE_INTEGRATION.md`
- **API Examples**: Code samples in integration guide
- **Langfuse Docs**: https://langfuse.com/docs
- **Dashboard**: https://cloud.langfuse.com

---

## 🎯 Next Steps

1. ✅ Start backend: `uvicorn app.main:app --reload`
2. ✅ Make a query: Use `/ask` endpoint
3. ✅ View trace: Find in Langfuse UI
4. ✅ Analyze span: Expand to see details
5. ✅ Set up alerts: Monitor for issues
6. ✅ Optimize: Use insights to improve performance

---

**Ready to go!** Start making queries and monitoring them in Langfuse. 🎉
