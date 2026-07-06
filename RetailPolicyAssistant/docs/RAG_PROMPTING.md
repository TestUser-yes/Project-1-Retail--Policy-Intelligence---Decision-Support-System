# RAG Prompting Guide

This document explains the standardized RAG (Retrieval-Augmented Generation) prompting system used in this project, following industry best practices.

## Problem Statement

A proper RAG prompt must have **two clear runtime inputs**:
1. **Context** - Retrieved documents from the retrieval pipeline
2. **Question** - The user's actual query

Without these, the LLM lacks the necessary information to generate accurate, grounded responses.

## Solution: Template-Based RAG Prompting

We implement 4 standardized RAG prompt patterns based on industry best practices:

### Pattern 1: Basic RAG (Default)
**When to use:** Simple queries, trusted context, standard use cases

**Structure:**
```
System Instructions: How to behave
    ↓
Context: {retrieved documents}
    ↓
Question: {user query}
    ↓
Answer: [LLM response]
```

**File:** `app/rag_pipeline/prompt_templates.py:BasicRAGTemplate`

**Code Example:**
```python
from app.rag_pipeline.prompt_templates import get_rag_template

template = get_rag_template("basic")
messages = template.format_prompt(context=retrieved_docs, question=user_query)
answer = llm.chat(messages)
```

### Pattern 2: Strict Grounding with Fallback
**When to use:** Accuracy is critical, hallucinations must be prevented

**Structure:**
```
System Instructions: STRICT RULES
    ↓
Context: {documents}
    ↓
Question: {query}
    ↓
Fallback: Clear "I couldn't find that information" instruction
    ↓
Answer: [LLM response, grounded only in provided context]
```

**Key Features:**
- Explicit prohibition on using outside knowledge
- Clear fallback instruction for missing information
- Rules: Don't guess, don't invent, don't infer

**File:** `app/rag_pipeline/prompt_templates.py:StrictGroundingTemplate`

**Usage:**
```python
template = get_rag_template("strict_grounding")
messages = template.format_prompt(context, question)
```

### Pattern 3: Structured Answer with Citation
**When to use:** Source attribution important, compliance/audit needs

**Structure:**
```
System Instructions: Structure answer with citations
    ↓
Context: {documents with sources}
    ↓
Question: {query}
    ↓
Required Response Format:
    1. Direct answer
    2. Quote from policy (with source)
    3. Compliance implications
    4. Source reference
    ↓
Answer: [Structured response with citations]
```

**Key Features:**
- Forces explicit source attribution
- Requires structured output format
- Includes compliance implications
- Audit-friendly

**File:** `app/rag_pipeline/prompt_templates.py:StructuredAnswerTemplate`

**Usage:**
```python
template = get_rag_template("structured_citation")
messages = template.format_prompt(context, question)
```

### Pattern 4: Multi-Chunk Synthesis
**When to use:** Multiple document chunks must be combined coherently

**Structure:**
```
System Instructions: Synthesize across documents
    ↓
Multiple Document Chunks: {doc1, doc2, doc3...}
    ↓
Question: {query}
    ↓
Instructions:
    - Combine information from all chunks
    - Avoid duplication
    - Reference each source
    - Handle conflicting info
    ↓
Answer: [Synthesized response]
```

**Key Features:**
- Encourages cross-document synthesis
- Prevents information duplication
- Handles conflicts between sources
- Clear source attribution for each part

**File:** `app/rag_pipeline/prompt_templates.py:MultiChunkSynthesisTemplate`

**Usage:**
```python
template = get_rag_template("multi_chunk_synthesis")
messages = template.format_prompt(context, question)
```

## Implementation Details

### 1. Template Architecture

All templates inherit from `BaseRAGTemplate`:

```python
from app.rag_pipeline.prompt_templates import BaseRAGTemplate

class CustomTemplate(BaseRAGTemplate):
    def get_name(self) -> str:
        return "custom_name"

    def get_description(self) -> str:
        return "When to use this template"

    def format_prompt(self, context: str, question: str) -> list:
        """Return list of message dicts for LLM."""
        return [
            {"role": "system", "content": "..."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"}
        ]
```

### 2. Runtime Input Injection

Context and question are injected at runtime:

```python
# DO THIS: Use templates for proper separation
template = get_rag_template("basic")
messages = template.format_prompt(
    context="[Retrieved documents here]",
    question="What is the policy?"
)
answer = llm.chat(messages)

# DON'T DO THIS: Hardcode prompts inline
prompt = f"Answer: {context}\nQ: {question}"  # ❌ No separation
```

### 3. LLM Service Integration

Updated `generate_rag_answer()` method:

```python
# In app/llm/service.py or app/llm/ollama_llm.py
def generate_rag_answer(self, question: str, context: str, template_pattern: str = "basic"):
    """Generate grounded RAG answer using templates."""
    template = get_rag_template(template_pattern)
    messages = template.format_prompt(context, question)
    return self.chat(messages)
```

### 4. Debug Logging

Each RAG call includes debug output showing:
- Template pattern selected
- Context length and preview
- User question
- Retrieved document chunks
- Response length

Example output:
```
============================================================
RAG GENERATION STARTED
Template Pattern: multi_chunk_synthesis
Context Length: 2847 characters
Question: What is the data retention policy?
============================================================

DEBUG: Retrieved Context (first 500 chars):
=========================DOCUMENT 1=========================
Document : Data_Retention_Policy.pdf
Page     : 3
Section  : Retention Requirements
...

============================================================
```

## Usage Examples

### Example 1: Simple Policy Question

```python
from app.rag_pipeline.prompt_templates import get_rag_template
from app.rag.context import build_context
from app.rag.retriever import retrieve_policy_chunks

question = "What is the data retention policy?"

# 1. Retrieve context
chunks = retrieve_policy_chunks(question)

# 2. Build context
context = build_context(chunks)

# 3. Select appropriate template
if len(chunks) > 1:
    template = get_rag_template("multi_chunk_synthesis")
else:
    template = get_rag_template("basic")

# 4. Generate messages
messages = template.format_prompt(context, question)

# 5. Get answer from LLM
answer = llm.chat(messages)
```

### Example 2: High-Accuracy Compliance Question

```python
# For critical compliance questions, use strict grounding
template = get_rag_template("strict_grounding")

# LLM service wrapper does this automatically:
answer = llm.generate_rag_answer(
    question="Is this vendor payment compliant with policy?",
    context=policy_documents,
    template_pattern="strict_grounding"  # Use grounding template
)
```

### Example 3: Audit-Friendly Structured Response

```python
# For audit trail requirements
template = get_rag_template("structured_citation")

messages = template.format_prompt(
    context="[Policy documents with section references]",
    question="What are the approval requirements?"
)

# Response will include:
# - Direct answer
# - Exact policy quote
# - Compliance implications
# - Source reference
```

## Files Modified

1. **Created:**
   - `app/rag_pipeline/prompt_templates.py` - Template implementations
   - `app/rag_pipeline/test_templates.py` - Template tests

2. **Updated:**
   - `app/prompts.py` - Added RAG template documentation
   - `app/llm/service.py` - Updated `generate_rag_answer()` with templates
   - `app/llm/ollama_llm.py` - Updated `generate_rag_answer()` with templates
   - `app/llm/base.py` - Updated base class signature
   - `app/rag/pipeline.py` - Uses new template system
   - `app/rag_pipeline/rag_pipeline.py` - Uses new template system
   - `app/agents/rag_agent.py` - Added debug logging

## Key Benefits

✅ **Proper RAG Structure** - Clear separation of system instructions, context, and question

✅ **Runtime Input Injection** - Context and question are runtime variables, not hardcoded

✅ **Multiple Patterns** - Choose the right template for your use case

✅ **Debug Visibility** - Know exactly what context and question are being sent to LLM

✅ **Prevents Hallucinations** - Strict grounding template prevents outside knowledge

✅ **Audit-Friendly** - Citation template includes source references

✅ **Synthesis Support** - Multi-chunk template intelligently combines documents

## Testing

Run template tests:
```bash
pytest app/rag_pipeline/test_templates.py -v
```

All 10 tests verify:
- Template availability and registry
- Proper context/question injection
- System instructions separation
- Debug-friendly formatting
- Empty context handling
- Placeholder functionality

## Migration from Old System

### Before (Old Way):
```python
# ❌ Hardcoded inline prompt
prompt = f"""Based on this context, answer the query:

Context:
{context}

Query: {query}

Answer:"""
```

### After (New Way):
```python
# ✅ Template-based with proper structure
template = get_rag_template("basic")
messages = template.format_prompt(context, query)
answer = llm.chat(messages)
```

## Best Practices

1. **Use the appropriate template:**
   - `basic` - Most queries
   - `strict_grounding` - Compliance questions
   - `structured_citation` - Audit requirements
   - `multi_chunk_synthesis` - Multiple document chunks

2. **Always pass runtime inputs:**
   ```python
   # Always pass context and question separately
   messages = template.format_prompt(
       context=retrieved_context,
       question=user_question
   )
   ```

3. **Debug RAG queries:**
   ```python
   # Enable debug output (automatic in generate_rag_answer)
   print(f"Context length: {len(context)}")
   print(f"Question: {question}")
   print(f"Template: {template.get_name()}")
   ```

4. **Handle empty context:**
   ```python
   if not context or not context.strip():
       return "No relevant documents found"
   ```

5. **Validate before LLM call:**
   ```python
   template = get_rag_template(pattern)  # Validates pattern exists
   messages = template.format_prompt(context, question)
   ```

## References

- [RAG Best Practices](https://www.anthropic.com/research)
- [Prompt Engineering Patterns](https://github.com/anthropics/prompt-optimization)
- Template implementations: `app/rag_pipeline/prompt_templates.py`
- Tests: `app/rag_pipeline/test_templates.py`
