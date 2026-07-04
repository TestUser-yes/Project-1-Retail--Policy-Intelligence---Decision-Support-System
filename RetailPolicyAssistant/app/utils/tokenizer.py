"""Token counting utility for accurate cost tracking."""

import os
from typing import Literal


def count_tokens(text: str, token_type: Literal["embedding", "completion"] = "completion") -> int:
    """
    Count tokens in text using appropriate tokenizer.

    Args:
        text: Text to tokenize
        token_type: Type of tokens (embedding or completion)

    Returns:
        Number of tokens
    """
    if not text:
        return 0

    # Try to use tiktoken (OpenAI tokenizer) if available
    try:
        import tiktoken

        if token_type == "embedding":
            # Embedding model uses cl100k_base encoding
            encoding = tiktoken.get_encoding("cl100k_base")
            tokens = encoding.encode(text)
            return len(tokens)
        else:
            # Completion models use cl100k_base encoding
            encoding = tiktoken.get_encoding("cl100k_base")
            tokens = encoding.encode(text)
            return len(tokens)
    except ImportError:
        # Fallback: approximate token count (rough estimate)
        # Average: ~4 characters per token
        return max(1, len(text) // 4)


def estimate_embedding_tokens(text: str) -> int:
    """Estimate tokens for embedding."""
    return count_tokens(text, "embedding")


def estimate_completion_tokens(text: str) -> int:
    """Estimate tokens for completion."""
    return count_tokens(text, "completion")


def count_query_response_tokens(query: str, response: str) -> tuple[int, int]:
    """
    Count tokens for query (embedding) and response (completion).

    Returns:
        (embedding_tokens, completion_tokens)
    """
    embedding_tokens = estimate_embedding_tokens(query)
    completion_tokens = estimate_completion_tokens(response)
    return embedding_tokens, completion_tokens


def get_provider_token_limits(provider: str) -> dict:
    """Get token limits for different providers."""
    limits = {
        "ollama": {
            "embedding_max_tokens": 384,  # Local model limit
            "completion_max_tokens": 2048,
        },
        "openai": {
            "embedding_max_tokens": 8191,
            "completion_max_tokens": 128000,
        },
        "anthropic": {
            "embedding_max_tokens": 8191,  # Claude doesn't have native embedding
            "completion_max_tokens": 200000,
        },
    }
    return limits.get(provider, limits["ollama"])


def validate_token_count(
    tokens: int, token_type: Literal["embedding", "completion"], provider: str
) -> bool:
    """Validate token count against provider limits."""
    limits = get_provider_token_limits(provider)
    key = f"{token_type}_max_tokens"
    max_tokens = limits.get(key, 2048)
    return tokens <= max_tokens
