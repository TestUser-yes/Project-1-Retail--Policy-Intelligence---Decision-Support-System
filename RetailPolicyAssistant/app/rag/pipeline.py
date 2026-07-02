from app.llm import LLMService
from app.rag.context import build_context
from app.rag.retriever import retrieve_policy_chunks

llm = LLMService()


def answer_policy_question(question: str):
    """
    Complete RAG pipeline:
    Question -> Retrieval -> Context -> LLM -> Response
    """
    chunks = retrieve_policy_chunks(question)
    if not chunks:
        return {
            "answer": "No relevant policy found.",
            "sources": [],
        }

    context = build_context(chunks)
    print("\n========== CONTEXT SENT TO LLM ==========")
    print(context)
    print("\n=========================================\n")
    answer = llm.generate_rag_answer(question, context)
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
