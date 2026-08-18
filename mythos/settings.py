"""Env-driven Mythos pipeline settings.

There is no Hermes ``config.py``. The live equivalent is this module plus
the ``M2M_*`` table in the README.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_PREREQ_CACHE_TTL_DAYS = 30


@dataclass(frozen=True)
class PipelineSettings:
    """Operator-tunable settings that used to live on a process-local cache."""

    prereq_cache_ttl_days: int = DEFAULT_PREREQ_CACHE_TTL_DAYS
    latex_deep_check: bool = False

    @classmethod
    def from_env(cls) -> "PipelineSettings":
        raw_ttl = os.getenv("M2M_PREREQ_CACHE_TTL_DAYS", str(DEFAULT_PREREQ_CACHE_TTL_DAYS))
        try:
            ttl = max(1, int(raw_ttl))
        except ValueError:
            ttl = DEFAULT_PREREQ_CACHE_TTL_DAYS
        deep = os.getenv("M2M_LATEX_DEEP_CHECK", "").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        return cls(prereq_cache_ttl_days=ttl, latex_deep_check=deep)
