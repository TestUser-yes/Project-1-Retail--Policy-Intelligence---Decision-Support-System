"""RAG Answer generation - retrieve and answer policy questions."""

from app.rag.retriever import retrieve_policy_chunks
from app.llm import LLMService


def answer_rag(query: str) -> dict:
    """
    Answer a query using RAG - retrieve relevant policy chunks and generate answer.

    Returns:
    {
        "answer": str,
        "sources": list of document chunks with metadata,
        "confidence": float
    }
    """
    llm = LLMService()

    # Retrieve relevant policy chunks
    chunks = retrieve_policy_chunks(query, top_k=6)

    if not chunks:
        return {
            "answer": "No relevant policy documents found for your query.",
            "sources": [],
            "confidence": 0.0,
        }

    # Format context from retrieved chunks
    context = "\n\n".join([
        f"[{chunk.document_name}] {chunk.content[:500]}"
        for chunk in chunks[:3]
    ])

    # Generate answer using LLM with context
    prompt = f"""You are a policy compliance expert. Answer the user's question based on the provided policy documents.

Policy Documents:
{context}

User Question: {query}

Provide a clear, concise answer citing the relevant policy sections."""

    response = llm.generate_json([
        {
            "role": "system",
            "content": "You are a helpful policy compliance assistant. Answer questions based on provided policies."
        },
        {
            "role": "user",
            "content": prompt
        }
    ])

    # Extract answer
    answer = response.get("answer", response.get("response", str(response)))

    return {
        "answer": answer,
        "sources": [
            {
                "document": chunk.document_name,
                "page": chunk.page_number,
                "section": chunk.section,
            }
            for chunk in chunks[:3]
        ],
        "confidence": 0.85,  # High confidence for RAG with sources
    }
