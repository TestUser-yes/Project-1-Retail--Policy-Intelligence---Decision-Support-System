from app.llm import LLMService
from app.rag.context import build_context
from app.rag.retriever import retrieve_policy_chunks
from app.rag.multi_agent_retrieval import retrieve_with_multi_agent
from app.observability.langfuse_tracer import trace_function

llm = LLMService()


@trace_function("rag_pipeline_with_multi_agent", as_type="chain")
def answer_policy_question(question: str, use_multi_agent: bool = True):
    """
    Complete RAG pipeline with optional multi-agent retrieval.

    Args:
        question: User query
        use_multi_agent: If True, uses multi-agent retrieval (default)
                        If False, uses single semantic retrieval (fallback)

    Returns:
        {
            "answer": Generated answer,
            "sources": Source documents,
            "retrieval_method": "multi_agent" or "semantic",
            "retrieval_details": Agent execution details (if multi_agent)
        }
    """
    # Use multi-agent retrieval by default
    if use_multi_agent:
        retrieval_result = retrieve_with_multi_agent(question, top_k=6)
        chunks = retrieval_result["documents"]
        retrieval_method = "multi_agent"
        retrieval_details = retrieval_result.get("retrieval_pipeline", {})
        agents_used = retrieval_result.get("agents_used", [])
    else:
        # Fallback to single semantic retrieval
        chunks = retrieve_policy_chunks(question)
        retrieval_method = "semantic"
        retrieval_details = {"method": "semantic_similarity"}
        agents_used = ["semantic_retrieval_agent"]

    if not chunks:
        return {
            "answer": "No relevant policy found.",
            "sources": [],
            "retrieval_method": retrieval_method,
            "retrieval_details": retrieval_details,
            "agents_used": agents_used,
        }

    context = build_context(chunks)

    print("\n" + "=" * 70)
    print("STANDARD RAG PIPELINE EXECUTION")
    print("=" * 70)
    print(f"\nRETRIEVED CONTEXT:")
    print(f"  - Number of chunks: {len(chunks)}")
    print(f"  - Total context length: {len(context)} characters")
    print(f"  - First chunk preview (first 300 chars):")
    print(context[:300] + "..." if len(context) > 300 else context)
    print("\n" + "=" * 70)
    print(f"USER QUESTION: {question}")
    print("=" * 70 + "\n")

    # Use standardized RAG template with best pattern for multi-chunk synthesis
    try:
        # Use multi_chunk_synthesis pattern if multiple chunks, else basic
        pattern = "multi_chunk_synthesis" if len(chunks) > 1 else "basic"
        answer = llm.generate_rag_answer(question, context, template_pattern=pattern)
    except Exception as e:
        print(f"RAG pipeline error: {e}")
        answer = f"Error generating answer: {str(e)}"

    return {
        "answer": answer,
        "sources": [
            {
                "document": chunk.document_name,
                "page": chunk.page_number,
                "section": chunk.section,
            }
            for chunk in chunks
        ],
        "retrieval_method": retrieval_method,
        "retrieval_details": retrieval_details,
        "agents_used": agents_used,
    }
