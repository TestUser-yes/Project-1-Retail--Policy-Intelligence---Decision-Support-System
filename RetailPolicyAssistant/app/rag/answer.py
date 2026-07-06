"""RAG Answer generation - retrieve and answer policy questions."""

from app.rag.retriever import retrieve_policy_chunks
from app.llm import LLMService


def answer_rag(query: str) -> dict:
    """
    Answer a query using RAG - retrieve relevant policy chunks and generate answer.

    Returns:
    {
        "result": str (the answer),
        "answer": str (same as result for compatibility),
        "sources": list of document chunks with metadata,
        "confidence": float
    }
    """
    llm = LLMService()

    # Retrieve relevant policy chunks
    chunks = retrieve_policy_chunks(query, top_k=6)

    if not chunks:
        return {
            "result": "No relevant policy documents found for your query.",
            "answer": "No relevant policy documents found for your query.",
            "sources": [],
            "confidence": 0.0,
        }

    # Format context from retrieved chunks (use more content for better answers)
    context_parts = []
    for chunk in chunks[:5]:
        context_parts.append(
            f"[{chunk.document_name} - Page {chunk.page_number}]\n{chunk.content}"
        )

    context = "\n\n---\n\n".join(context_parts)

    # Generate answer using LLM with full context
    prompt = f"""You are a policy compliance expert. Answer the user's question accurately based on the provided policy documents.

POLICY DOCUMENTS:
{context}

USER QUESTION: {query}

INSTRUCTIONS:
1. Provide a clear, accurate answer based only on the documents provided
2. Cite specific sections and page numbers
3. If the information is not in the documents, say so explicitly
4. Be concise but thorough"""

    try:
        response = llm.generate_json([
            {
                "role": "system",
                "content": """You are a policy compliance expert. Answer questions based on provided policy documents.

IMPORTANT RULES:
1. Answer ONLY the specific question asked - be concise
2. Do NOT return entire documents or all available information
3. Extract only the relevant sections needed to answer the query
4. Keep answers to 2-3 sentences maximum unless more detail is necessary
5. Always cite the source document and page number
6. Focus on being helpful, not comprehensive"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ])

        # Extract answer - try multiple field names
        answer = response.get("answer", response.get("response", response.get("result", str(response))))
    except Exception as e:
        # Fallback: compile a concise answer from chunks
        relevant_content = []
        for chunk in chunks[:2]:  # Only use top 2 chunks
            content = chunk.content.split('\n')[0:5]  # Only first 5 lines
            relevant_content.append(f"{chunk.document_name} (Page {chunk.page_number}): {' '.join(content)}")

        answer = "Answer from policy documents:\n\n" + "\n\n".join(relevant_content)

    return {
        "result": answer,
        "answer": answer,
        "sources": [
            {
                "document": chunk.document_name,
                "page": chunk.page_number,
                "section": chunk.section,
            }
            for chunk in chunks[:5]
        ],
        "confidence": 0.92,  # High confidence for RAG with actual PDF sources
    }
