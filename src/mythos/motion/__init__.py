"""The ``motion`` profile chain: a motion-design brief in, a checked video out.

    1 brief parser   -> BriefSpec   (backends.run_model, typed)
    2 art director   -> StyleSheet  (backends.run_model, typed)
    3 storyboard     -> Timeline    (backends.run_model, typed)
    4 scene coder    -> scene.py    (Claude Agent SDK session, drafts + frames)
    5 render + QA    -> QAReport    (harness render, probe/pixel checks, QA agent)
    6 repair         -> scene.py    (same SDK session), back to 5, at most 4 loops

Every action is a trace event (:mod:`mythos.trace`) in ``events.jsonl``.
"""

from mythos.motion.pipeline import MotionHarness

__all__ = ["MotionHarness"]
