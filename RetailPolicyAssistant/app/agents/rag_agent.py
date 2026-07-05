from app.rag import answer_rag


class RAGAgent:
    """RAG agent that retrieves policies and returns sources."""

    def run(self, query: str) -> dict:
        """Run RAG query and return structured result."""
        try:
            result = answer_rag(query)
            if result and "not found" not in result.lower() and "error" not in result.lower():
                confidence = 0.90
            else:
                confidence = 0.4

            return {
                "result": result,
                "sources": ["Policy Database"],
                "confidence": confidence,
            }
        except Exception as e:
            print(f"RAG Agent error: {e}")
            return {
                "result": f"Error retrieving policy: {str(e)}",
                "sources": [],
                "confidence": 0.0,
            }
