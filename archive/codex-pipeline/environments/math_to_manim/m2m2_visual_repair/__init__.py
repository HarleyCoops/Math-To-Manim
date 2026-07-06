"""Math-To-Manim visual repair Verifiers environment."""

from .scoring import ScoreResult, score_completion

__all__ = ["ScoreResult", "load_environment", "score_completion"]


def load_environment(*args, **kwargs):
    """Load the Verifiers environment without importing heavy deps at package import time."""

    from .environment import load_environment as _load_environment

    return _load_environment(*args, **kwargs)
