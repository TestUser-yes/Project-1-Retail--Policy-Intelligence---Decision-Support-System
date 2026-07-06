# RAG Prompting Quick Reference

## How to Use

### Basic Usage
```python
from app.rag_pipeline.prompt_templates import get_rag_template

# Select template
template = get_rag_template("basic")

# Format with context and question
messages = template.format_prompt(
    context="[DOCUMENT 1] Policy content here",
    question="What is the policy?"
)

# Send to LLM
answer = llm.chat(messages)
```

### With LLM Service (Recommended)
```python
answer = llm.generate_rag_answer(
    question="What is the policy?",
    context=retrieved_documents,
    template_pattern="basic"  # optional, defaults to "basic"
)
```

## Template Quick Reference

| Pattern | Use Case | Feature |
|---------|----------|---------|
| `basic` | Most queries | Simple, clear structure |
| `strict_grounding` | Compliance, high-accuracy | Prevents hallucinations with explicit fallback |
| `structured_citation` | Audit, citations needed | Returns structured response with sources |
| `multi_chunk_synthesis` | Multiple documents | Intelligently combines chunks without duplication |

## Examples by Use Case

### Scenario 1: Simple Policy Question
```python
# User asks: "What is the retention policy?"
question = "What is the retention policy?"

# Retrieve documents
chunks = retrieve_policy_chunks(question)
context = build_context(chunks)

# Use basic template (default)
answer = llm.generate_rag_answer(question, context)
```

### Scenario 2: Compliance Question (Prevent Hallucinations)
```python
# User asks: "Is this practice compliant?"
question = "Is this practice compliant with policy?"

chunks = retrieve_policy_chunks(question)
context = build_context(chunks)

# Use strict grounding to prevent outside knowledge
answer = llm.generate_rag_answer(
    question, context,
    template_pattern="strict_grounding"
)
```

### Scenario 3: Audit Trail with Citations
```python
# User asks: "What are the requirements?"
question = "What are the approval requirements?"

chunks = retrieve_policy_chunks(question)
context = build_context(chunks)

# Use structured citation for audit trail
answer = llm.generate_rag_answer(
    question, context,
    template_pattern="structured_citation"
)
# Response includes: answer, quote with source, compliance notes
```

### Scenario 4: Combining Multiple Documents
```python
# Automatic when multiple chunks retrieved
chunks = retrieve_policy_chunks(query)

if len(chunks) > 1:
    # Multi-chunk synthesis pattern (see app/rag/pipeline.py)
    template = get_rag_template("multi_chunk_synthesis")
else:
    template = get_rag_template("basic")

messages = template.format_prompt(context, question)
```

## Template Structure

Each template has this structure:

```
System Role: Static instructions (how to behave)
  ├─ Never invent information
  ├─ Cite sources
  └─ Keep answers concise

User Role: Runtime inputs
  ├─ Context (from retrieval)
  └─ Question (from user)
```

## Debug Output

Enable debug output to see what's being sent to LLM:

```python
answer = llm.generate_rag_answer(question, context)

# Automatically prints:
# - Which template pattern
# - Context length and preview
# - User question
# - Response length
```

Output example:
```
============================================================
RAG GENERATION STARTED
Template Pattern: multi_chunk_synthesis
Context Length: 2847 characters
Question: What is the data retention policy?
============================================================

DEBUG: Retrieved Context (first 500 chars):
[DOCUMENT 1] Data_Retention_Policy.pdf...

============================================================
LLM Response Length: 543 characters
============================================================
```

## Common Patterns

### Pattern: Detect and Handle Missing Context
```python
from app.rag_pipeline.prompt_templates import get_rag_template

context = build_context(chunks)

# Validate context exists
if not context or not context.strip():
    return "No relevant documents found"

# Safe to use template
template = get_rag_template("basic")
messages = template.format_prompt(context, question)
```

### Pattern: Select Template by Query Type
```python
def select_template(question: str, num_chunks: int) -> str:
    """Auto-select template based on query characteristics."""
    
    if "compliant" in question.lower() or "allowed" in question.lower():
        return "strict_grounding"  # Compliance questions
    
    if num_chunks > 1:
        return "multi_chunk_synthesis"  # Multiple documents
    
    if "cite" in question.lower() or "source" in question.lower():
        return "structured_citation"  # Citation needed
    
    return "basic"  # Default

# Usage
pattern = select_template(user_question, len(chunks))
template = get_rag_template(pattern)
```

### Pattern: Add Custom Context Headers
```python
def enhance_context(chunks):
    """Add structured headers for clarity."""
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(
            f"[DOCUMENT {i}] {chunk.document_name} (p.{chunk.page_number})\n"
            f"Section: {chunk.section}\n"
            f"Content:\n{chunk.content}"
        )
    return "\n\n".join(parts)

# Usage
context = enhance_context(chunks)
template = get_rag_template("basic")
messages = template.format_prompt(context, question)
```

## Error Handling

```python
from app.rag_pipeline.prompt_templates import get_rag_template

try:
    template = get_rag_template("strict_grounding")
except KeyError as e:
    print(f"Invalid template: {e}")
    template = get_rag_template("basic")  # Fallback to default

try:
    answer = llm.generate_rag_answer(question, context)
except ValueError as e:
    print(f"Invalid input: {e}")
    answer = "Unable to answer question"
```

## Testing

Test a template:
```python
from app.rag_pipeline.prompt_templates import get_rag_template

template = get_rag_template("basic")

# Format with test data
messages = template.format_prompt(
    context="[DOCUMENT] Test content",
    question="Test question?"
)

# Verify structure
assert len(messages) == 2
assert messages[0]["role"] == "system"
assert messages[1]["role"] == "user"
assert "[DOCUMENT] Test content" in messages[1]["content"]
assert "Test question?" in messages[1]["content"]
```

## Available Methods

```python
# Get a template
template = get_rag_template("pattern_name")

# Template methods
template.get_name()           # Returns "basic", etc.
template.get_description()    # Returns "When to use..."
template.format_prompt(context, question)  # Returns message list

# Utility functions
from app.rag_pipeline.prompt_templates import list_rag_templates

templates = list_rag_templates()
# Returns: [{"name": "basic", "description": "..."}, ...]
```

## Files to Know

- **Definitions**: `app/rag_pipeline/prompt_templates.py`
- **Tests**: `app/rag_pipeline/test_templates.py`
- **Integration**: `app/rag/pipeline.py` and `app/llm/service.py`
- **Docs**: `RAG_PROMPTING.md`, `BEFORE_AND_AFTER.md`

## Troubleshooting

### Q: Template not found
```python
# Error: KeyError: "Template 'xyz' not found"
# Solution: Use one of the 4 available patterns
valid_patterns = ["basic", "strict_grounding", "structured_citation", "multi_chunk_synthesis"]
template = get_rag_template(valid_patterns[0])
```

### Q: Context not being used by LLM
```python
# Ensure context is not empty and properly formatted
if not context or not context.strip():
    print("ERROR: No context provided")
    return

# Check context is in the message
messages = template.format_prompt(context, question)
user_msg = messages[1]["content"]
assert context in user_msg, "Context not in message"
```

### Q: LLM ignoring context instructions
```python
# Use strict_grounding pattern which has explicit rules
template = get_rag_template("strict_grounding")
# This pattern has multiple explicit rules like:
# - "CRITICAL RULES - NEVER VIOLATE"
# - "Never use any outside knowledge"
# - Clear fallback instructions
```

### Q: How to debug what's sent to LLM?
```python
# Debug output is automatic in generate_rag_answer()
answer = llm.generate_rag_answer(question, context)

# Also prints:
# - Template pattern used
# - Context length and preview
# - Question asked
# - Response length

# For manual debugging:
from app.rag_pipeline.prompt_templates import get_rag_template
template = get_rag_template("basic")
messages = template.format_prompt(context, question)
import json
print(json.dumps(messages, indent=2))
```

## Next: Learn More

1. **Detailed Guide**: Read `RAG_PROMPTING.md`
2. **Before/After**: Read `BEFORE_AND_AFTER.md`
3. **Implementation**: Read `IMPLEMENTATION_SUMMARY.md`
4. **Source Code**: Review `app/rag_pipeline/prompt_templates.py`
5. **Tests**: Read `app/rag_pipeline/test_templates.py`

---

**Last Updated**: 2026-07-05
**Status**: Production Ready ✓
