from app.rag import answer_rag


class RAGAgent:
    """RAG agent that retrieves policies and returns sources."""

    def run(self, query: str):
        """Run RAG query and return structured result."""
        try:
            result = answer_rag(query)
            return {
                "result": result,
                "sources": ["Policy Database"],
                "confidence": 0.85,
            }
        except Exception as e:
            print(f"RAG Agent error: {e}")
            return {
                "result": f"Error retrieving policy: {str(e)}",
                "sources": [],
                "confidence": 0.0,
            }
