"""Query Rewriter - Step 1 of RAG pipeline: Query enhancement."""

from app.llm import LLMService


class QueryRewriter:
    """Rewrites user queries for better retrieval."""

    def __init__(self):
        self.llm = LLMService()

    def rewrite_query(self, original_query: str) -> dict:
        """Rewrite query to improve retrieval quality."""
        prompt = f"""Rewrite this query to be more specific for policy document retrieval:
Query: {original_query}

Return JSON with:
- original: original query
- rewritten: improved query
- terms: key terms extracted
"""
        result = self.llm.generate_json([
            {"role": "system", "content": "You are a query optimization expert."},
            {"role": "user", "content": prompt}
        ])
        return result

    def expand_query(self, query: str) -> list:
        """Generate query variations for better coverage."""
        return [query]  # TODO: Implement query expansion

    def get_keywords(self, query: str) -> list:
        """Extract key terms from query."""
        return query.split()
