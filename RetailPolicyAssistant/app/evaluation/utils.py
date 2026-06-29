from __future__ import annotations

import json
import math
from typing import Any


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return " ".join(normalize_text(item) for item in value)
    if isinstance(value, dict):
        for key in ("answer", "result", "summary", "text", "content", "response"):
            if key in value:
                return normalize_text(value[key])
        return json.dumps(value, default=str, ensure_ascii=True)
    return str(value)


def contains_keywords(text: str, keywords: list[str]) -> tuple[bool, list[str]]:
    normalized_text = text.lower()
    missing = [keyword for keyword in keywords if keyword.lower() not in normalized_text]
    return len(missing) == 0, missing


def coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "y"}:
            return True
        if lowered in {"false", "0", "no", "n"}:
            return False
    return bool(value)


def p95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil(0.95 * len(ordered)) - 1)
    return float(ordered[index])

