"""RFC 7396 JSON Merge Patch without input mutation."""

from __future__ import annotations

from copy import deepcopy

from pydantic import JsonValue


def apply_merge_patch(target: JsonValue, patch: JsonValue) -> JsonValue:
    """Return ``target`` with an RFC 7396 merge patch applied."""

    if not isinstance(patch, dict):
        return deepcopy(patch)

    result = deepcopy(target) if isinstance(target, dict) else {}
    for key, value in patch.items():
        if value is None:
            result.pop(key, None)
        else:
            result[key] = apply_merge_patch(result.get(key), value)
    return result


__all__ = ["apply_merge_patch"]
