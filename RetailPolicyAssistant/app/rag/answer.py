"""RAG Answer generation - retrieve and answer policy questions."""

from app.rag.retriever import retrieve_policy_chunks
from app.rag.multi_agent_retrieval import retrieve_with_multi_agent
from app.llm import LLMService
from app.prompts import get_rag_template


def _extract_answer_from_chunks(chunks, query: str) -> str:
    """Extract a concise answer from chunks without using LLM.

    Falls back to intelligent extraction when LLM service is unavailable.
    Extracts first 2-3 sentences that are most relevant to the query.
    """
    if not chunks:
        return "Error: No chunks available"

    query_lower = query.lower()

    # Extract key terms from query
    query_words = set(word for word in query_lower.split() if len(word) > 3)

    best_sentences = []
    sentence_count = 0

    # Look through chunks for relevant sentences
    for chunk in chunks[:2]:  # Only use first 2 chunks for speed
        content = chunk.content
        sentences = [s.strip() for s in content.split('. ') if s.strip()]

        for sentence in sentences:
            # Score sentence by matching query words
            sentence_lower = sentence.lower()
            matches = sum(1 for word in query_words if word in sentence_lower)

            if matches > 0 or sentence_count < 2:  # Include at least 2 sentences
                best_sentences.append(sentence)
                sentence_count += 1

                if sentence_count >= 3:  # Stop after 3 sentences
                    break

        if sentence_count >= 3:
            break

    if not best_sentences:
        # Fallback: just take first sentences from first chunk
        sentences = [s.strip() for s in chunks[0].content.split('. ') if s.strip()]
        best_sentences = sentences[:3]

    # Join sentences with proper punctuation
    answer = '. '.join(best_sentences)
    if not answer.endswith('.'):
        answer += '.'

    return answer.replace('..', '.')


def answer_rag(query: str, use_multi_agent: bool = True) -> dict:
    """
    Answer a query using RAG with optional multi-agent retrieval.

    Args:
        query: User question
        use_multi_agent: If True, uses multi-agent retrieval (semantic + keyword)
                        If False, uses single semantic retrieval (fallback)

    Returns:
    {
        "result": str (the answer - 2-3 sentences maximum),
        "answer": str (same as result for compatibility),
        "sources": list of document chunks with metadata,
        "confidence": float (0.92 for PDF-backed answers),
        "documents": list of retrieved documents,
        "retrieval_method": "multi_agent" or "semantic",
        "retrieval_details": agent execution details,
        "agents_used": list of retrieval agent names
    }
    """
    llm = LLMService()

    # Retrieve relevant policy chunks using multi-agent approach
    if use_multi_agent:
        retrieval_result = retrieve_with_multi_agent(query, top_k=6)
        chunks = retrieval_result["documents"]
        retrieval_method = "multi_agent"
        retrieval_details = retrieval_result.get("retrieval_pipeline", {})
        agents_used = retrieval_result.get("agents_used", [])
    else:
        # Fallback to single semantic retrieval
        chunks = retrieve_policy_chunks(query, top_k=6)
        retrieval_method = "semantic"
        retrieval_details = {"method": "semantic_similarity"}
        agents_used = ["semantic_retrieval_agent"]

    if not chunks:
        return {
            "result": "No relevant policy documents found for your query.",
            "answer": "No relevant policy documents found for your query.",
            "sources": [],
            "confidence": 0.0,
            "documents": [],
            "retrieval_method": retrieval_method,
            "retrieval_details": retrieval_details,
            "agents_used": agents_used,
        }

    # Format context from top 3 chunks only (not 5) to force conciseness
    context_parts = []
    for chunk in chunks[:3]:
        context_parts.append(
            f"[{chunk.document_name} - Page {chunk.page_number}]\n{chunk.content}"
        )

    context = "\n\n---\n\n".join(context_parts)

    # Use standardized RAG template for consistency
    template = get_rag_template("strict_grounding")
    messages = template.format_prompt(context, query)

    # Add strict conciseness instruction to user message
    messages[-1]["content"] += "\n\nIMPORTANT: Keep your answer to 2-3 sentences maximum. Be concise."

    try:
        # Call LLM with template-formatted messages
        response = llm.chat(messages, temperature=0.2)

        # Clean up response
        answer = response.strip()

        # Enforce hard limit: if response is too long, truncate to first 2-3 sentences
        sentences = answer.split('. ')
        if len(sentences) > 3:
            # Keep only first 3 sentences
            answer = '. '.join(sentences[:3]) + '.'
            answer = answer.replace('..', '.')  # Fix any double periods

    except Exception as e:
        # Fallback: Extract answer from chunks without LLM (when LLM unavailable)
        # This is a smart extraction that works without any LLM service
        answer = _extract_answer_from_chunks(chunks, query)

        if not answer or answer.startswith("Error"):
            # If extraction also failed, show informative message
            answer = f"Could not connect to LLM service. Retrieved {len(chunks)} relevant policy documents but unable to synthesize answer. Please try again later or contact support."

    return {
        "result": answer,
        "answer": answer,
        "sources": [
            {
                "document": chunk.document_name,
                "page": chunk.page_number,
                "section": chunk.section,
            }
            for chunk in chunks[:3]  # Only top 3 sources
        ],
        "confidence": 0.92,  # High confidence for RAG with actual PDF sources
        "documents": chunks,  # Raw documents for orchestrator
        "retrieval_method": retrieval_method,
        "retrieval_details": retrieval_details,
        "agents_used": agents_used,
    }
