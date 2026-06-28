from app.agents.rag_agent import RAGAgent
from app.agents.sql_agent import SQLAgent


class HybridAgent:
    def __init__(self):
        self.rag_agent = RAGAgent()
        self.sql_agent = SQLAgent()

    def run(self, query: str):
        return {
            "rag": self.rag_agent.run(query),
            "sql": self.sql_agent.run(query),
            "summary": "combined insights generated"
        }
