# Quick Start Guide - Ingestion & Retrieval Endpoints

## 30-Second Overview

Two new endpoints for managing policy documents:
- **Phase 1: `/api/ingestion/ingest`** - Upload PDF → Index
- **Phase 2: `/api/ingestion/retrieve`** - Query → Search chunks

## Installation

```bash
# Install missing dependency (if needed)
pip install python-multipart
```

## Running the Server

```bash
cd RetailPolicyAssistant
uvicorn app.main:app --reload --port 8000
```

Visit: `http://localhost:8000/docs` for interactive API documentation

## Basic Usage

### 1. Get Token
```bash
TOKEN=$(curl -s http://localhost:8000/token | jq -r '.access_token')
echo $TOKEN
```

### 2. Phase 1: Ingest a PDF
```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@Documents/Anti_Bribery_Ethical_Conduct_Policy.pdf" \
  http://localhost:8000/api/ingestion/ingest | jq
```

Response:
```json
{
  "filename": "Anti_Bribery_Ethical_Conduct_Policy.pdf",
  "chunks_created": 45,
  "total_pages": 12,
  "status": "indexed"
}
```

### 3. Phase 2: Retrieve Chunks
```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the ethical conduct policies?",
    "k": 3
  }' \
  http://localhost:8000/api/ingestion/retrieve | jq
```

Response:
```json
{
  "query": "What are the ethical conduct policies?",
  "chunks": [
    {
      "content": "...",
      "metadata": {
        "document_name": "policy.pdf",
        "page_number": 2,
        "section": "1. Introduction"
      }
    }
  ],
  "count": 3
}
```

## Automatic Testing

```bash
python test_ingestion_endpoints.py
```

Runs through complete flow:
- Gets token
- Tests Phase 1 (ingestion)
- Tests Phase 2 (retrieval)

## What Gets Stored

After ingestion, documents are indexed in PostgreSQL:

```sql
SELECT document_name, COUNT(*) as chunks
FROM policy_documents
GROUP BY document_name;

-- Output:
-- document_name                            | chunks
-- Anti_Bribery_Ethical_Conduct_Policy.pdf |     45
```

## Python Example

```python
import requests

# Setup
BASE_URL = "http://localhost:8000"
token_resp = requests.get(f"{BASE_URL}/token")
token = token_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Phase 1: Ingest
with open("policy.pdf", "rb") as f:
    ingest = requests.post(
        f"{BASE_URL}/api/ingestion/ingest",
        files={"file": f},
        headers=headers
    )
print(f"Ingested: {ingest.json()['chunks_created']} chunks")

# Phase 2: Retrieve
retrieve = requests.post(
    f"{BASE_URL}/api/ingestion/retrieve",
    json={"query": "What are the policies?", "k": 3},
    headers=headers
)
for chunk in retrieve.json()["chunks"]:
    print(f"- {chunk['metadata']['document_name']}: {chunk['content'][:50]}...")
```

## JavaScript Example

```javascript
const BASE_URL = "http://localhost:8000";

// Get token
const tokenResp = await fetch(`${BASE_URL}/token`);
const { access_token } = await tokenResp.json();
const headers = { Authorization: `Bearer ${access_token}` };

// Phase 1: Ingest (assuming file input element exists)
const file = document.querySelector('input[type="file"]').files[0];
const formData = new FormData();
formData.append("file", file);
const ingestResp = await fetch(`${BASE_URL}/api/ingestion/ingest`, {
  method: "POST",
  headers,
  body: formData
});
console.log(`Ingested: ${(await ingestResp.json()).chunks_created} chunks`);

// Phase 2: Retrieve
const retrieveResp = await fetch(`${BASE_URL}/api/ingestion/retrieve`, {
  method: "POST",
  headers: { ...headers, "Content-Type": "application/json" },
  body: JSON.stringify({ query: "What are the policies?", k: 3 })
});
const data = await retrieveResp.json();
data.chunks.forEach(chunk => {
  console.log(`- ${chunk.metadata.document_name}: ${chunk.content.substring(0, 50)}...`);
});
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Not authenticated" | Get new token: `curl http://localhost:8000/token` |
| "Only PDF files are supported" | Upload a .pdf file, not .txt |
| "No chunks retrieved" | Ingest a PDF first, then retrieve |
| "Connection refused" | Start server: `uvicorn app.main:app --reload` |
| "User does not have permission" | Contact admin to grant ASK_POLICY_QUESTION permission |

## Files to Reference

- **API Reference:** `API_ENDPOINTS_REFERENCE.md` (complete endpoint docs)
- **Architecture:** `INGESTION_RETRIEVAL_FLOW.md` (detailed design)
- **Implementation:** `IMPLEMENTATION_SUMMARY.md` (technical overview)
- **Flow:** `FLOW_COMPARISON.md` (how it matches requirements)
- **Code:** `app/routers/ingestion.py` (endpoint implementation)

## Integration with /ask

The endpoints work with your existing `/ask` flow:

```
/ingest Endpoint
  ↓ (adds documents)
PostgreSQL policy_documents table
  ↑ (queried by)
/ask Endpoint ← Uses retrieve_policy_chunks()
/retrieve Endpoint ← Uses same retrieve_policy_chunks()
```

All three endpoints use the same indexed documents and embedding space.

## Performance

- **Ingest:** 2-5 seconds per 12-page PDF
- **Retrieve:** 100-300ms for top-6 chunks
- **Embedding:** 100-200ms per chunk (depends on provider)

---

For complete documentation: See referenced files above

For support: Check error response messages for specific issues
