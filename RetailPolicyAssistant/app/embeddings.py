from __future__ import annotations

import hashlib
import os
import re

import numpy as np


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
    return _fallback_embedding(text)
