"""Query Result Caching for Performance

Caches query results and embeddings to improve response latency.
Uses in-memory cache for demo, extensible to Redis.
"""

import hashlib
import time
from typing import Any, Dict, Optional, Tuple
from datetime import datetime, timezone, timedelta


class CacheEntry:
    """Single cache entry with TTL."""

    def __init__(self, key: str, value: Any, ttl_seconds: int = 3600):
        """Initialize cache entry.

        Args:
            key: Cache key
            value: Cached value
            ttl_seconds: Time-to-live in seconds (default 1 hour)
        """
        self.key = key
        self.value = value
        self.created_at = time.time()
        self.ttl_seconds = ttl_seconds
        self.hit_count = 0

    def is_expired(self) -> bool:
        """Check if entry expired.

        Returns:
            True if expired
        """
        return (time.time() - self.created_at) > self.ttl_seconds

    def get_age_seconds(self) -> float:
        """Get age of entry in seconds.

        Returns:
            Age in seconds
        """
        return time.time() - self.created_at

    def to_dict(self) -> Dict:
        """Convert to dictionary for inspection."""
        return {
            "key": self.key,
            "created_at": datetime.fromtimestamp(self.created_at, timezone.utc).isoformat(),
            "ttl_seconds": self.ttl_seconds,
            "age_seconds": self.get_age_seconds(),
            "hit_count": self.hit_count,
            "expired": self.is_expired(),
        }


class QueryCache:
    """In-memory cache for query results."""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """Initialize query cache.

        Args:
            max_size: Maximum cache entries
            default_ttl: Default time-to-live in seconds
        """
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
        }

    def _make_key(self, query: str, context: str = None) -> str:
        """Generate cache key from query and context.

        Args:
            query: Query string
            context: Optional context for differentiation

        Returns:
            Cache key
        """
        key_source = f"{query}:{context}" if context else query
        return hashlib.sha256(key_source.encode()).hexdigest()

    def get(self, query: str, context: str = None) -> Optional[Any]:
        """Get cached result.

        Args:
            query: Query string
            context: Optional context

        Returns:
            Cached value or None
        """
        key = self._make_key(query, context)

        if key not in self.cache:
            self.stats["misses"] += 1
            return None

        entry = self.cache[key]

        # Check expiration
        if entry.is_expired():
            del self.cache[key]
            self.stats["misses"] += 1
            return None

        entry.hit_count += 1
        self.stats["hits"] += 1
        return entry.value

    def set(self, query: str, value: Any, context: str = None, ttl_seconds: int = None) -> None:
        """Cache a query result.

        Args:
            query: Query string
            value: Value to cache
            context: Optional context
            ttl_seconds: Override default TTL
        """
        key = self._make_key(query, context)
        ttl = ttl_seconds or self.default_ttl

        # Evict old entry if needed
        if len(self.cache) >= self.max_size:
            self._evict_lru()

        self.cache[key] = CacheEntry(key, value, ttl)

    def clear(self) -> None:
        """Clear entire cache."""
        self.cache.clear()

    def get_stats(self) -> Dict:
        """Get cache statistics.

        Returns:
            Dict with hit rate, miss rate, size
        """
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate_percent": hit_rate,
            "evictions": self.stats["evictions"],
            "total_requests": total_requests,
        }

    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if not self.cache:
            return

        # Find entry with lowest hit count (proxy for LRU)
        lru_key = min(self.cache.keys(), key=lambda k: self.cache[k].hit_count)
        del self.cache[lru_key]
        self.stats["evictions"] += 1


class EmbeddingCache:
    """Cache for embedding vectors."""

    def __init__(self, max_entries: int = 10000):
        """Initialize embedding cache.

        Args:
            max_entries: Maximum embeddings to cache
        """
        self.embeddings: Dict[str, Tuple[int, Any]] = {}  # doc_id -> (timestamp, embedding)
        self.max_entries = max_entries

    def get_embedding(self, doc_id: str) -> Optional[Any]:
        """Get cached embedding.

        Args:
            doc_id: Document ID

        Returns:
            Embedding vector or None
        """
        if doc_id not in self.embeddings:
            return None
        return self.embeddings[doc_id][1]

    def cache_embedding(self, doc_id: str, embedding: Any) -> None:
        """Cache an embedding.

        Args:
            doc_id: Document ID
            embedding: Embedding vector
        """
        if len(self.embeddings) >= self.max_entries:
            # Remove oldest entry
            oldest_key = min(self.embeddings.keys(), key=lambda k: self.embeddings[k][0])
            del self.embeddings[oldest_key]

        self.embeddings[doc_id] = (time.time(), embedding)

    def clear(self) -> None:
        """Clear cache."""
        self.embeddings.clear()

    def get_size(self) -> int:
        """Get number of cached embeddings."""
        return len(self.embeddings)


# Global caches
_query_cache = None
_embedding_cache = None


def get_query_cache() -> QueryCache:
    """Get global query cache instance."""
    global _query_cache
    if _query_cache is None:
        _query_cache = QueryCache(max_size=1000, default_ttl=3600)
    return _query_cache


def get_embedding_cache() -> EmbeddingCache:
    """Get global embedding cache instance."""
    global _embedding_cache
    if _embedding_cache is None:
        _embedding_cache = EmbeddingCache(max_entries=10000)
    return _embedding_cache


# Helper functions

def cache_query_result(query: str, result: Any, context: str = None, ttl_seconds: int = 3600) -> None:
    """Cache a query result.

    Args:
        query: Query string
        result: Result to cache
        context: Optional context
        ttl_seconds: Time-to-live
    """
    cache = get_query_cache()
    cache.set(query, result, context, ttl_seconds)


def get_cached_query_result(query: str, context: str = None) -> Optional[Any]:
    """Get cached query result if available.

    Args:
        query: Query string
        context: Optional context

    Returns:
        Cached result or None
    """
    cache = get_query_cache()
    return cache.get(query, context)


def cache_embedding(doc_id: str, embedding: Any) -> None:
    """Cache an embedding.

    Args:
        doc_id: Document ID
        embedding: Embedding vector
    """
    cache = get_embedding_cache()
    cache.cache_embedding(doc_id, embedding)


def get_cached_embedding(doc_id: str) -> Optional[Any]:
    """Get cached embedding.

    Args:
        doc_id: Document ID

    Returns:
        Cached embedding or None
    """
    cache = get_embedding_cache()
    return cache.get_embedding(doc_id)


def clear_all_caches() -> None:
    """Clear all caches."""
    get_query_cache().clear()
    get_embedding_cache().clear()
