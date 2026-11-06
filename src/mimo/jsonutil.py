"""JSON extraction helpers for MiMo tool-calling replies."""

from __future__ import annotations

import json
import re
from typing import Any


def extract_json_object(text: str) -> dict[str, Any]:
    """Return the first JSON object found in ``text``.

    Prefers fenced ```json blocks, then bare object spans.
    """
    if not text or not text.strip():
        raise ValueError("empty model reply")
    fenced = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        return json.loads(fenced.group(1))
    fenced_any = re.search(r"```\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced_any:
        return json.loads(fenced_any.group(1))
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("no JSON object in model reply")
    return json.loads(text[start : end + 1])


def dump_json(payload: Any) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=False)
