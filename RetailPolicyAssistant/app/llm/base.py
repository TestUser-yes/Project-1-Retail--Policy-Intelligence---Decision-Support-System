from abc import ABC, abstractmethod


class BaseLLM(ABC):
    @abstractmethod
    def chat(self, messages, temperature: float = 0.2):
        pass

    @abstractmethod
    def generate_json(self, messages, temperature: float = 0.2):
        pass

    @abstractmethod
    def generate_rag_answer(self, question: str, context: str, template_pattern: str = "basic"):
        """Generate answer using RAG template.

        Args:
            question: User's query
            context: Retrieved documents
            template_pattern: Which template pattern to use (basic, strict_grounding, etc.)
        """
        pass
