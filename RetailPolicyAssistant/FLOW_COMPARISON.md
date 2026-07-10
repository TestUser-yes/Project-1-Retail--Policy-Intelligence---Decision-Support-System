# Flow Comparison: Your Screenshots vs Implementation

## Your Requirement (from Screenshots)

### Left Screenshot - Data Ingestion Phase
```
┌─────────────┐
│ PDF File    │
│ Upload      │
└──────┬──────┘
       ↓
┌─────────────────────┐
│  DATA INGESTION     │
├─────────────────────┤
│ 1. Load PDF         │
│    (PyPDFLoader)    │
│                     │
│ 2. Split into       │
│    chunks           │
│    (RecursiveChar   │
│     TextSplitter)   │
│                     │
│ 3. Embed each       │
│    chunk            │
│    (OpenAI/Ollama)  │
│                     │
│ 4. Store in         │
│    PostgreSQL       │
│    with pgvector    │
└──────┬──────────────┘
       ↓
┌──────────────────────┐
│ Embedded Chunks      │
│ in Database          │
│ (policy_documents)   │
└──────────────────────┘
```

### Right Screenshot - Data Retrieval Phase
```
┌──────────────────┐
│ User Query       │
│ "What does      │
│  LangChain...?" │
└────────┬─────────┘
         ↓
┌─────────────────────┐
│ DATA RETRIEVAL      │
├─────────────────────┤
│ 1. Embed query      │
│    (get_embedding)  │
│                     │
│ 2. Vector Search    │
│    (ANN with        │
│     pgvector)       │
│                     │
│ 3. Return top-k     │
│    chunks with      │
│    metadata         │
└────────┬────────────┘
         ↓
┌──────────────────────┐
│ Retrieved Chunks     │
│ - Content            │
│ - Document Name      │
│ - Page Number        │
│ - Section            │
└──────────────────────┘
```

---

## Implementation Mapping

### Phase 1: Data Ingestion ✅

| Screenshot Component | Implementation |
|---|---|
| **PDF Upload** | `POST /api/ingestion/ingest` with multipart form |
| **Load PDF** | PyPDFLoader in `index_pdf_file()` |
| **Split chunks** | RecursiveCharacterTextSplitter (1000 chars, 200 overlap) |
| **Embed** | `get_embedding()` → OpenAI/Ollama/fallback |
| **Store in DB** | PolicyDocument ORM model with pgvector |
| **Response** | IngestResponse with chunks_created, pages, status |

**Endpoint Request:**
```bash
POST /api/ingestion/ingest
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <PDF>
```

**Endpoint Response:**
```json
{
  "filename": "policy.pdf",
  "chunks_created": 45,
  "total_pages": 12,
  "status": "indexed",
  "timestamp": "2026-07-10T15:30:45.123456"
}
```

**Code Flow:**
```
ingest_document()
  ├─ Validate auth & permissions
  ├─ Save uploaded file
  ├─ Call index_pdf_file()
  │   ├─ PyPDFLoader.load()
  │   ├─ RecursiveCharacterTextSplitter.split_text()
  │   ├─ get_embedding() for each chunk
  │   └─ db.add(PolicyDocument(...))
  ├─ db.commit()
  ├─ Log to Langfuse
  └─ Return IngestResponse
```

---

### Phase 2: Data Retrieval ✅

| Screenshot Component | Implementation |
|---|---|
| **User Query Input** | `POST /api/ingestion/retrieve` with JSON |
| **Embed Query** | `get_embedding(query)` |
| **Vector Search (ANN)** | `retrieve_policy_chunks()` with pgvector L2 distance |
| **Return Chunks** | ChunkData model with metadata |
| **Metadata** | id, document_name, page_number, section, chunk_number |

**Endpoint Request:**
```bash
POST /api/ingestion/retrieve
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "What does LangChain use to store vectors?",
  "k": 6
}
```

**Endpoint Response:**
```json
{
  "query": "What does LangChain use to store vectors?",
  "chunks": [
    {
      "content": "Vectors are stored in a PostgreSQL database...",
      "metadata": {
        "id": 1,
        "document_name": "policy.pdf",
        "page_number": 2,
        "section": "1. Introduction",
        "chunk_number": 1
      }
    }
  ],
  "count": 6,
  "timestamp": "2026-07-10T15:35:22.654321"
}
```

**Code Flow:**
```
retrieve_documents()
  ├─ Validate auth & permissions
  ├─ get_embedding(query)
  ├─ Call retrieve_policy_chunks()
  │   ├─ PolicyDocument.embedding.l2_distance(query_embedding)
  │   └─ .order_by(...).limit(k*2)
  ├─ Format chunks with metadata
  ├─ Log to Langfuse
  └─ Return RetrieveResponse
```

---

## Side-by-Side Comparison

### Ingestion Process

| Step | Your Flow | Our Implementation |
|------|-----------|-------------------|
| 1 | User uploads PDF | `POST /api/ingestion/ingest` |
| 2 | PDF loaded from upload | `PyPDFLoader(temp_file)` |
| 3 | Split into chunks | `RecursiveCharacterTextSplitter` |
| 4 | Generate embeddings | `get_embedding()` per chunk |
| 5 | Store in database | `PolicyDocument` with pgvector |
| 6 | Return status | `IngestResponse` with metadata |

### Retrieval Process

| Step | Your Flow | Our Implementation |
|------|-----------|-------------------|
| 1 | User enters query | `POST /api/ingestion/retrieve` |
| 2 | Query embedded | `get_embedding(query)` |
| 3 | Vector search performed | `retrieve_policy_chunks()` |
| 4 | Top-k results selected | `.limit(k*2)` then slice `[:k]` |
| 5 | Results ranked by similarity | Ordered by L2 distance |
| 6 | Return with metadata | `RetrieveResponse` with ChunkData |

---

## Integration with Existing System

The new endpoints work alongside your existing `/ask` endpoint:

```
User Interface
    │
    ├─ POST /ask
    │  (Query → RAG → Answer)
    │  ├─ Orchestrator.run()
    │  ├─ retrieve_policy_chunks() ← Uses same function
    │  ├─ LLM generation
    │  └─ Returns: answer + sources
    │
    ├─ POST /api/ingestion/ingest
    │  (Upload → Index)
    │  ├─ index_pdf_file()
    │  └─ Returns: ingestion status
    │
    └─ POST /api/ingestion/retrieve
       (Query → Search)
       ├─ retrieve_policy_chunks()
       └─ Returns: raw chunks
```

**Key Point:** `/ingest` adds documents to the same database table that `/ask` uses. They share the same embedding space and retrieval function.

---

## Example End-to-End Flow

```bash
# Step 1: Get auth token
TOKEN=$(curl -s http://localhost:8000/token | jq -r '.access_token')

# Step 2: Upload a policy document
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@Documents/Anti_Bribery_Ethical_Conduct_Policy.pdf" \
  http://localhost:8000/api/ingestion/ingest
# Response: {"chunks_created": 45, "status": "indexed"}

# Step 3: Test retrieval (Phase 2)
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"What are the ethical conduct policies?","k":3}' \
  http://localhost:8000/api/ingestion/retrieve
# Response: {"chunks": [...], "count": 3}

# Step 4: Use /ask to get intelligent answer (integration test)
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"What are the ethical conduct policies?"}' \
  http://localhost:8000/ask
# Response: {"answer": "...", "sources": [...]}
```

---

## Database Schema

Your flow requires the `policy_documents` table, which already exists:

```sql
CREATE TABLE policy_documents (
    id SERIAL PRIMARY KEY,
    document_name VARCHAR(255) NOT NULL,      -- From /ingest upload
    page_number INTEGER NOT NULL,             -- From PDF loader
    chunk_number INTEGER NOT NULL,            -- From splitter
    section VARCHAR(255),                     -- Metadata
    content TEXT NOT NULL,                    -- From splitter
    embedding vector(1536),                   -- From embeddings (Phase 1)
    created_at TIMESTAMP DEFAULT NOW()
);

-- For fast vector search (Phase 2)
CREATE INDEX ON policy_documents 
    USING ivfflat (embedding vector_cosine_ops);
```

Both phases use this table:
- **Phase 1:** Inserts new rows with embeddings
- **Phase 2:** Reads rows and performs similarity search

---

## API Specifications Match

Your flow describes the operations needed. Our endpoints implement exactly what you require:

### Phase 1 Checklist ✅
- [x] Load PDF from upload
- [x] Split into chunks
- [x] Generate embeddings
- [x] Store in database
- [x] Return ingestion status

### Phase 2 Checklist ✅
- [x] Accept user query
- [x] Embed query
- [x] Perform vector search
- [x] Return top-k results
- [x] Include chunk metadata

---

## Testing Your Flow

### Verify Phase 1
```bash
# After ingestion, check database has chunks
psql $DATABASE_URL -c "SELECT COUNT(*) FROM policy_documents;"
# Should show > 0 rows

# Check embeddings are stored
psql $DATABASE_URL -c "SELECT id, embedding::text FROM policy_documents LIMIT 1;"
# Should show 1536-dim vector
```

### Verify Phase 2
```bash
# Run retrieval test
python test_ingestion_endpoints.py

# Should show:
# PHASE 1: DATA INGESTION TEST
# [OK] Ingestion successful
# PHASE 2: DATA RETRIEVAL TEST
# [OK] Retrieved X chunks
```

---

## Success Criteria ✅

- [x] Both phases implemented as separate API endpoints
- [x] Phase 1 follows: Load → Split → Embed → Store flow
- [x] Phase 2 follows: Query → Embed → Search → Return flow
- [x] Uses PDF documents (not sample.txt)
- [x] Leverages pgvector for similarity search
- [x] Works alongside existing /ask endpoint
- [x] No confusion with existing endpoints
- [x] Comprehensive documentation
- [x] Automated test script provided
- [x] Production-ready code patterns

---

## Conclusion

Your flow requirements have been precisely implemented:

**Left Screenshot (Data Ingestion)** → `/api/ingestion/ingest` endpoint
**Right Screenshot (Data Retrieval)** → `/api/ingestion/retrieve` endpoint

Both follow your architectural vision, integrate with the existing system, and are ready for production use.
