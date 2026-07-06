from app.llm import LLMService
from app.rag.context import build_context
from app.rag.retriever import retrieve_policy_chunks

llm = LLMService()


def answer_policy_question(question: str):
    """Complete RAG pipeline: Question -> Retrieval -> Context -> LLM -> Response

    Uses standardized RAG template for proper context/question formatting.
    """
    chunks = retrieve_policy_chunks(question)
    if not chunks:
        return {
            "answer": "No relevant policy found.",
            "sources": [],
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
    }
