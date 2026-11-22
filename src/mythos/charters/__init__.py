"""Prompt profiles: which charter and which stage chain a run uses.

- ``math`` (default): the Mythos Cinematic Charter and the six-stage
  explanation chain (:mod:`mythos.stages`). Unchanged.
- ``motion``: the Motion Charter and the brief-to-video chain
  (:mod:`mythos.motion`) for product and motion-design briefs, where the brief
  is a specification to meet rather than an idea to explain.
"""

from __future__ import annotations

from dataclasses import dataclass

from mythos.charters import math_profile as _math
from mythos.charters import motion as _motion

DEFAULT_PROFILE = "math"


@dataclass(frozen=True)
class Profile:
    name: str
    charter: str
    summary: str


PROFILES: dict[str, Profile] = {
    "math": Profile("math", _math.CHARTER, _math.SUMMARY),
    "motion": Profile("motion", _motion.CHARTER, _motion.SUMMARY),
}

PROFILE_NAMES: tuple[str, ...] = tuple(PROFILES)


def get_profile(name: str | None) -> Profile:
    """The profile called ``name`` (None means the default)."""
    key = (name or DEFAULT_PROFILE).strip().lower()
    try:
        return PROFILES[key]
    except KeyError:
        raise ValueError(
            f"unknown profile {name!r}; choose one of: {', '.join(PROFILE_NAMES)}") from None
