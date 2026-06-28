from app.llm import LLMService

llm = LLMService()


class RouterAgent:
    """
    Decides execution path with reasoning
    """

    def run(self, intent_result: dict):
        intent = intent_result.get("intent", "rag")

        return {
            "route": intent,
            "decision": "route selected by agent"
        }