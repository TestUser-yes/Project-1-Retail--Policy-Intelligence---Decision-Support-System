# API Endpoints Reference - Ingestion & Retrieval

## Quick Start

### 1. Get Authentication Token
```bash
curl http://localhost:8000/token
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

---

## Phase 1: POST /api/ingestion/ingest

### Description
Upload a PDF document for indexing. The document is:
1. Loaded from PDF
2. Split into chunks (1000 chars, 200 overlap)
3. Embedded as vectors (1536 dimensions)
4. Stored in PostgreSQL with pgvector

### Request

**Method:** `POST`  
**Path:** `/api/ingestion/ingest`  
**Authentication:** Required (Bearer token)  
**Content-Type:** `multipart/form-data`

**Parameters:**
```
file: UploadFile (PDF file, required)
```

### Example Request

```bash
TOKEN="your_bearer_token_here"

curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@Documents/Anti_Bribery_Ethical_Conduct_Policy.pdf" \
  http://localhost:8000/api/ingestion/ingest
```

### Example Response (Success)

```json
{
  "filename": "Anti_Bribery_Ethical_Conduct_Policy.pdf",
  "document_name": "Anti_Bribery_Ethical_Conduct_Policy.pdf",
  "chunks_created": 45,
  "total_pages": 12,
  "status": "indexed",
  "timestamp": "2026-07-10T15:30:45.123456"
}
```

### Error Responses

**400 Bad Request - Invalid File Format**
```json
{
  "detail": "Only PDF files are supported"
}
```

**400 Bad Request - Empty File**
```json
{
  "detail": "Uploaded file is empty"
}
```

**401 Unauthorized - Missing Token**
```json
{
  "detail": "Not authenticated"
}
```

**403 Forbidden - Insufficient Permissions**
```json
{
  "detail": "User does not have permission to ASK_POLICY_QUESTION"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Ingestion failed: [error details]"
}
```

### HTTP Status Codes
| Code | Meaning |
|------|---------|
| 200 | Successfully indexed document |
| 400 | Invalid file or request format |
| 401 | Authentication failed |
| 403 | User lacks required permissions |
| 500 | Server error during indexing |

---

## Phase 2: POST /api/ingestion/retrieve

### Description
Search for relevant document chunks using semantic vector similarity.
Returns top-k most relevant chunks with full metadata.

### Request

**Method:** `POST`  
**Path:** `/api/ingestion/retrieve`  
**Authentication:** Required (Bearer token)  
**Content-Type:** `application/json`

**Request Body:**
```json
{
  "query": "string (required, 1-1000 chars)",
  "k": "integer (optional, default 6, range 1-20)"
}
```

### Example Request

```bash
TOKEN="your_bearer_token_here"

curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the ethical conduct policies?",
    "k": 3
  }' \
  http://localhost:8000/api/ingestion/retrieve
```

### Example Response (Success)

```json
{
  "query": "What are the ethical conduct policies?",
  "chunks": [
    {
      "content": "An ethical conduct policy outlines the principles and standards expected of all employees...",
      "metadata": {
        "id": 1,
        "document_name": "Anti_Bribery_Ethical_Conduct_Policy.pdf",
        "page_number": 2,
        "section": "1. Introduction",
        "chunk_number": 1
      }
    },
    {
      "content": "Employees must maintain the highest standards of integrity and honesty in all business dealings...",
      "metadata": {
        "id": 2,
        "document_name": "Anti_Bribery_Ethical_Conduct_Policy.pdf",
        "page_number": 3,
        "section": "2. Core Principles",
        "chunk_number": 2
      }
    },
    {
      "content": "Conflicts of interest must be disclosed immediately to the compliance department...",
      "metadata": {
        "id": 3,
        "document_name": "Anti_Bribery_Ethical_Conduct_Policy.pdf",
        "page_number": 5,
        "section": "3. Conflict of Interest",
        "chunk_number": 4
      }
    }
  ],
  "count": 3,
  "timestamp": "2026-07-10T15:35:22.654321"
}
```

### Error Responses

**400 Bad Request - Query Too Short**
```json
{
  "detail": "Query must be at least 1 character"
}
```

**400 Bad Request - Query Too Long**
```json
{
  "detail": "Query must be no more than 1000 characters"
}
```

**400 Bad Request - Invalid k Value**
```json
{
  "detail": "k must be between 1 and 20"
}
```

**401 Unauthorized - Missing Token**
```json
{
  "detail": "Not authenticated"
}
```

**403 Forbidden - Insufficient Permissions**
```json
{
  "detail": "User does not have permission to ASK_POLICY_QUESTION"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Retrieval failed: [error details]"
}
```

### HTTP Status Codes
| Code | Meaning |
|------|---------|
| 200 | Successfully retrieved chunks |
| 400 | Invalid query or parameters |
| 401 | Authentication failed |
| 403 | User lacks required permissions |
| 500 | Server error during retrieval |

---

## Response Models

### IngestResponse

```json
{
  "filename": "string (uploaded file name)",
  "document_name": "string (name in database)",
  "chunks_created": "integer (number of chunks)",
  "total_pages": "integer (pages in PDF)",
  "status": "string (indexed, error, etc.)",
  "timestamp": "string (ISO 8601 format)"
}
```

### RetrieveResponse

```json
{
  "query": "string (original search query)",
  "chunks": [
    {
      "content": "string (chunk text)",
      "metadata": {
        "id": "integer",
        "document_name": "string",
        "page_number": "integer",
        "section": "string",
        "chunk_number": "integer"
      }
    }
  ],
  "count": "integer (number of chunks returned)",
  "timestamp": "string (ISO 8601 format)"
}
```

---

## Usage Examples

### Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Get token
token_resp = requests.get(f"{BASE_URL}/token")
token = token_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Ingest a PDF
with open("sample.pdf", "rb") as f:
    files = {"file": f}
    ingest_resp = requests.post(
        f"{BASE_URL}/api/ingestion/ingest",
        files=files,
        headers=headers
    )
    print(ingest_resp.json())

# Retrieve chunks
retrieve_resp = requests.post(
    f"{BASE_URL}/api/ingestion/retrieve",
    json={"query": "What are the policies?", "k": 5},
    headers=headers
)
chunks = retrieve_resp.json()
for chunk in chunks["chunks"]:
    print(f"[{chunk['metadata']['document_name']}] {chunk['content'][:100]}...")
```

### JavaScript/Fetch

```javascript
const BASE_URL = "http://localhost:8000";

// Get token
const tokenResp = await fetch(`${BASE_URL}/token`);
const { access_token } = await tokenResp.json();
const headers = { Authorization: `Bearer ${access_token}` };

// Ingest a PDF
const formData = new FormData();
formData.append("file", document.querySelector('input[type="file"]').files[0]);
const ingestResp = await fetch(`${BASE_URL}/api/ingestion/ingest`, {
  method: "POST",
  headers,
  body: formData
});
const ingestData = await ingestResp.json();
console.log(ingestData);

// Retrieve chunks
const retrieveResp = await fetch(`${BASE_URL}/api/ingestion/retrieve`, {
  method: "POST",
  headers: { ...headers, "Content-Type": "application/json" },
  body: JSON.stringify({ query: "What are the policies?", k: 5 })
});
const chunks = await retrieveResp.json();
chunks.chunks.forEach(chunk => {
  console.log(chunk.metadata.document_name, chunk.content);
});
```

### cURL

```bash
# Store token in variable
TOKEN=$(curl -s http://localhost:8000/token | jq -r '.access_token')

# Ingest
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@Documents/policy.pdf" \
  http://localhost:8000/api/ingestion/ingest | jq

# Retrieve
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"What are the policies?","k":5}' \
  http://localhost:8000/api/ingestion/retrieve | jq
```

---

## Testing

### Automated Test Script

```bash
python test_ingestion_endpoints.py
```

This script will:
1. Get authentication token
2. Test ingestion with sample PDF
3. Test retrieval with multiple queries
4. Display results for each phase

---

## Integration with /ask Endpoint

The `/ingest` and `/retrieve` endpoints work alongside the main `/ask` endpoint:

```
/ask Endpoint (Complete RAG Flow):
  POST /ask {"query": "What are the policies?"}
    → /retrieve internally (retrieve_policy_chunks)
    → LLM generation with retrieved chunks
    → Returns final answer + sources

/retrieve Endpoint (Debugging):
  POST /api/ingestion/retrieve {"query": "...", "k": 6}
    → Returns raw chunks for inspection
    → Useful for tuning retrieval quality

/ingest Endpoint (Document Management):
  POST /api/ingestion/ingest (file)
    → Adds new documents to knowledge base
    → /ask queries can then use these documents
```

---

## Performance Notes

| Operation | Typical Latency |
|-----------|-----------------|
| Token generation | <100ms |
| PDF ingestion (12 pages) | 2-5 seconds |
| Embedding generation per chunk | 100-200ms |
| Vector similarity search | 50-200ms |
| Total retrieval latency | 100-300ms |

---

## Rate Limiting

- **Ingestion** (`/ingest`): Limited per user (prevents abuse)
- **Retrieval** (`/retrieve`): High throughput (design for queries)
- **Ask** (`/ask`): Standard rate limits apply

---

## Security Notes

1. **Authentication Required**: Both endpoints require valid JWT token
2. **Permission Checks**: Validates `ASK_POLICY_QUESTION` permission
3. **Input Validation**: Query length limits, file type validation
4. **Error Messages**: Don't expose internal system details
5. **Langfuse Tracing**: All operations logged for audit trail

---

## Troubleshooting

### "Ingestion failed: No such file or directory"
- Check PDF file exists and is readable
- Ensure `Documents/` folder exists

### "Retrieval failed: No documents found"
- Ingest at least one PDF using `/ingest` endpoint
- Check `policy_documents` table has records

### "Connection refused: localhost:8000"
- Ensure backend server is running: `uvicorn app.main:app --reload`

### "Not authenticated" or "Invalid token"
- Get fresh token: `curl http://localhost:8000/token`
- Include in header: `Authorization: Bearer <token>`

### "User does not have permission"
- Check user role and permissions in database
- Contact admin to grant ASK_POLICY_QUESTION permission
