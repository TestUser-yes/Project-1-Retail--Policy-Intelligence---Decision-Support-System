from app.rag import answer_from_policy_context


class RAGAgent:
    """RAG agent that retrieves policies and returns sources."""

    def run(self, query: str):
        """Run RAG query and return structured result with sources."""
        try:
            rag_result = answer_from_policy_context(query)
            return {
                "result": rag_result.answer,
                "sources": rag_result.sources,
                "confidence": rag_result.confidence,
            }
        except Exception as e:
            print(f"RAG Agent error: {e}")
            return {
                "result": f"Error retrieving policy: {str(e)}",
                "sources": [],
                "confidence": 0.0,
            }
