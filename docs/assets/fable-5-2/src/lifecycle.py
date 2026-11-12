"""lifecycle.png: the job and run lifecycles added in commit a49352e.

States, legal moves and outcomes are read from ``mythos.lifecycle``. The
"after" manifest is read from ``data/job_records.json`` (see
``capture_job_records.py``). The "before" manifest is that same manifest
without the fields the commit added.

Usage:  .venv\\Scripts\\python.exe docs\\assets\\fable-5-2\\src\\lifecycle.py
Writes: docs/assets/fable-5-2/lifecycle.png
"""

from __future__ import annotations

import json
from pathlib import Path

from mythos.lifecycle import JOB_TRANSITIONS, JobStatus, RunOutcome, RunStatus
from mythos.stages import STAGES

import style as S
from diagram import Canvas, text_width

RECORDS = json.loads(
    (Path(__file__).resolve().parent / "data" / "job_records.json").read_text(encoding="utf-8"))

# Meanings: the comments on RunOutcome in src/mythos/lifecycle.py.
OUTCOME_MEANING = {
    RunOutcome.FILM_READY: "Rendered. The video exists.",
    RunOutcome.SCENE_READY: "Scene code passed checks. Render was not requested.",
    RunOutcome.VALIDATION_FAILED: "Scene code failed static checks.",
    RunOutcome.RENDER_FAILED: "manim exited non-zero. Repairs are used up.",
    RunOutcome.RENDER_TIMED_OUT: "Render went over its time budget.",
    RunOutcome.RENDER_BLOCKED: "The machine lacks manim, TeX or ffmpeg.",
    RunOutcome.CHAIN_FAILED: "An exception stopped the chain.",
}
GOOD = {RunOutcome.FILM_READY, RunOutcome.SCENE_READY}
BUILD_STEPS = ("codegen", "verify", "render", "repair")


def main() -> None:
    assert set(OUTCOME_MEANING) == set(RunOutcome) and len(RunOutcome) == 7
    Q, R, C, F = JobStatus.QUEUED, JobStatus.RUNNING, JobStatus.COMPLETED, JobStatus.FAILED
    assert JOB_TRANSITIONS == {Q: {R, F}, R: {C, F}, C: set(), F: set()}
    assert {s.value for s in RunStatus} >= {"running", "completed", "failed"}

    c = Canvas(height=1508)
    top = c.header(
        "What changed: explicit job and run lifecycles",
        "Commit a49352e, src/mythos/lifecycle.py. A job and a run now say where they are "
        "and how they ended.",
        "NOW", S.OLIVE)

    # ---------------- A: job status ---------------------------------------
    ax, aw, ah = S.MARGIN, 716, 396
    y = c.panel(ax, top, aw, ah, "Job status", "JOB_TRANSITIONS: the only legal moves")
    bh = 60

    def state(x, cy, w, name, outline):
        c.box(x, cy - bh / 2, w, bh, fill=S.PANEL_HI, outline=outline)
        c.text(x + w / 2, cy, name, "mono", S.LABEL, S.IVORY, "mm")

    cy_mid = y + 78
    cy_top, cy_bot = cy_mid - 46, cy_mid + 46
    qx, qw, rx_, rw_, fx, fw = ax + 24, 150, ax + 254, 164, ax + 496, 196
    state(qx, cy_mid, qw, Q.value, S.FOG)
    state(rx_, cy_mid, rw_, R.value, S.FOG)
    state(fx, cy_top, fw, C.value, S.OLIVE)
    state(fx, cy_bot, fw, F.value, S.CORAL)
    c.arrow([(qx + qw, cy_mid), (rx_, cy_mid)])
    elbow = (rx_ + rw_ + fx) / 2
    c.arrow([(rx_ + rw_, cy_mid - 14), (elbow, cy_mid - 14), (elbow, cy_top), (fx, cy_top)],
            fill=S.OLIVE)
    c.arrow([(rx_ + rw_, cy_mid + 14), (elbow, cy_mid + 14), (elbow, cy_bot), (fx, cy_bot)],
            fill=S.CORAL)
    low = cy_bot + bh / 2 + 24
    c.arrow([(qx + qw / 2, cy_mid + bh / 2), (qx + qw / 2, low), (fx + fw / 2, low),
             (fx + fw / 2, cy_bot + bh / 2)], fill=S.CORAL)
    c.text(ax + 24, top + ah - 76, "Any other move raises IllegalTransition.",
           "regular", S.NOTE, S.FOG)
    c.text(ax + 24, top + ah - 44, "completed and failed are final.", "regular", S.NOTE, S.FOG)

    # ---------------- B: run stage ----------------------------------------
    bx = ax + aw + 24
    bw = c.width - S.MARGIN - bx
    y = c.panel(bx, top, bw, ah, "Run stage",
                "status.stage in manifest.json: the step running now")
    slugs = [stage.slug for stage in STAGES]
    rows = [slugs[:3], slugs[3:], list(BUILD_STEPS)]
    for r, names in enumerate(rows):
        x = bx + 24
        for name in names:
            x += c.chip(x, y + r * 52, name, S.LINE if r < 2 else S.FOG) + 10
        assert x < bx + bw - 14
    note_y = top + ah - 108
    c.runs(bx + 24, note_y, [("status.run", "mono", S.NOTE, S.IVORY),
                             (" is running, completed or failed.", "regular", S.NOTE, S.FOG)])
    c.text(bx + 24, note_y + 32, "A completed run has no stage.", "regular", S.NOTE, S.FOG)
    c.text(bx + 24, note_y + 64, "A failed run keeps it: the step that failed.",
           "regular", S.NOTE, S.FOG)

    # ---------------- C: run outcome --------------------------------------
    cy0 = top + ah + 24
    row_h = 46
    ch = 104 + 7 * row_h + 18
    y = c.panel(S.MARGIN, cy0, c.width - 2 * S.MARGIN, ch, "Run outcome",
                "status.outcome in manifest.json and in each job record. "
                "One value says how a finished run ended.")
    for i, outcome in enumerate(RunOutcome):
        mid = y + i * row_h + row_h / 2
        if i:
            c.line([(S.MARGIN + 24, mid - row_h / 2), (c.width - S.MARGIN - 24, mid - row_h / 2)],
                   fill=S.LINE, width=1)
        color = S.OLIVE if outcome in GOOD else S.CORAL
        c.dot(S.MARGIN + 36, mid, 7, color)
        c.text(S.MARGIN + 60, mid, outcome.value, "mono", S.LABEL, S.IVORY)
        c.text(S.MARGIN + 380, mid, OUTCOME_MEANING[outcome], "regular", S.NOTE, S.FOG)
        tag = {RunOutcome.FILM_READY: "film",
               RunOutcome.SCENE_READY: "checked scene, no film"}.get(outcome, "no film")
        c.text(c.width - S.MARGIN - 24, mid, tag, "regular", S.NOTE, color, "rm")

    # ---------------- D: before and after ---------------------------------
    dy = cy0 + ch + 24
    dh = 422
    half = (c.width - 2 * S.MARGIN - 24) / 2
    manifest = RECORDS["failed"]["manifest"]
    status = manifest["status"]
    assert status["run"] == "failed" and status["outcome"] == "chain_failed"
    added = ("run", "stage", "outcome")
    before = {k: v for k, v in status.items() if k not in added}

    def code_panel(x, title, note, lines, footer):
        y0 = c.panel(x, dy, half, dh, title, note)
        for i, (line, strong) in enumerate(lines):
            mid = y0 + i * 31 + 15
            if strong:
                c.line([(x + 24, mid - 12), (x + 24, mid + 12)], fill=S.CORAL, width=3)
            assert text_width(line, "mono", S.NOTE) < half - 64, line
            c.text(x + 40, mid, line, "mono", S.NOTE, S.IVORY if strong else S.FOG)
        for i, line in enumerate(footer):
            c.text(x + 24, dy + dh - 26 - (len(footer) - 1 - i) * 32, line,
                   "regular", S.NOTE, S.FOG)

    def status_lines(block: dict) -> list[tuple[str, bool]]:
        out = [('"status": {', False)]
        items = list(block.items())
        for i, (key, value) in enumerate(items):
            comma = "," if i < len(items) - 1 else ""
            out.append((f'  "{key}": {json.dumps(value)}{comma}', key in added))
        return out

    code_panel(
        S.MARGIN, "Before: a crashed run",
        "manifest.json for the same crash, without the new fields",
        status_lines(before) + [("}", False)],
        ["Nothing says the run stopped.",
         "On disk it is the same as a run in progress."])
    code_panel(
        S.MARGIN + half + 24, "After: the same crash",
        "manifest.json from a run with a stub model backend",
        status_lines(status) + [("},", False),
                                (f'"error": {json.dumps(manifest["error"])},', True),
                                (f'"failed_utc": {json.dumps(manifest["failed_utc"])}', True)],
        ["The run is recorded as failed, with the step that failed."])

    c.save("lifecycle.png")


if __name__ == "__main__":
    main()
