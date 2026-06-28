from __future__ import annotations

import hashlib
import os
import re

import numpy as np
from openai import OpenAI


api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None


def _fallback_embedding(text: str, dimensions: int = 1536) -> list[float]:
    """
    Deterministic local embedding used when the OpenAI API is unavailable.
    """
    vector = np.zeros(dimensions, dtype=float)
    tokens = re.findall(r"[a-z0-9]+", text.lower())

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
        index = int(digest[:8], 16) % dimensions
        vector[index] += 1.0

    norm = np.linalg.norm(vector)
    if norm:
        vector = vector / norm

    return vector.tolist()


def get_embedding(text: str):
    """
    Convert text → vector embedding
    """
    if client is None:
        return _fallback_embedding(text)

    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return response.data[0].embedding
    except Exception:
        return _fallback_embedding(text)
