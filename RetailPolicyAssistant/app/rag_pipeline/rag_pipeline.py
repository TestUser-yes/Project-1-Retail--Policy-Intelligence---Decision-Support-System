"""RAG Pipeline - Orchestrates all 6 steps of Retrieval-Augmented Generation."""

from app.rag_pipeline.query_rewriter import QueryRewriter
from app.rag_pipeline.embeddings import EmbeddingService
from app.rag_pipeline.retriever import Retriever
from app.rag_pipeline.reranker import Reranker
from app.rag_pipeline.context_compressor import ContextCompressor
from app.llm import LLMService


class RAGPipeline:
    """End-to-end RAG pipeline with 6 steps."""

    def __init__(self):
        self.rewriter = QueryRewriter()
        self.embeddings = EmbeddingService()
        self.retriever = Retriever()
        self.reranker = Reranker()
        self.compressor = ContextCompressor()
        self.llm = LLMService()

    async def run(self, query: str) -> dict:
        """Execute full RAG pipeline."""
        # Step 1: Query Rewriting
        rewritten = self.rewriter.rewrite_query(query)
        
        # Step 2: Embeddings
        query_embedding = self.embeddings.embed_query(rewritten.get("rewritten", query))
        
        # Step 3: Vector Search (Retrieval)
        documents = self.retriever.retrieve_hybrid(
            query_embedding,
            rewritten.get("terms", [])
        )
        
        # Step 4: Reranking
        reranked = self.reranker.rerank(query, documents)
        
        # Step 5: Context Compression
        context = self.compressor.compress_context(reranked)
        
        # Step 6: LLM Generation
        answer = await self._generate_answer(query, context)

        return {
            "query": query,
            "rewritten_query": rewritten.get("rewritten", query),
            "retrieved_documents": len(documents),
            "reranked_documents": len(reranked),
            "context_length": len(context),
            "answer": answer,
            "confidence": 0.85,
        }

    async def _generate_answer(self, query: str, context: str) -> str:
        """Generate answer from context using LLM with standardized RAG template from app.prompts."""
        if not context or not context.strip():
            return "No relevant context available to answer the query."

        print("\n" + "=" * 60)
        print("RAG PIPELINE: GENERATING ANSWER")
        print(f"Query: {query}")
        print(f"Context chunks: {context.count('DOCUMENT')}")
        print("=" * 60)

        try:
            # Use standardized RAG template from app.prompts
            answer = await self.llm.generate_rag_answer(query, context, template_pattern="basic")
            return answer
        except Exception as e:
            print(f"Error generating answer: {e}")
            return f"Unable to generate answer: {str(e)}"
