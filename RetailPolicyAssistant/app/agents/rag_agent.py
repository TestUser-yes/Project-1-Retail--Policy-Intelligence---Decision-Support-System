from app.rag import answer_rag


class RAGAgent:
    def run(self, query: str):
        return {
            "result": answer_rag(query)
        }
