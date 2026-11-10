"""mcp.png: how an agent uses the Mythos MCP server (commit 9e154fd).

Tool names are read from the registered server in ``mythos.mcp_server``.
The job records are the JSON that ``m2m_get_job`` returned, read from
``data/job_records.json`` (see ``capture_job_records.py``).

Usage:  .venv\\Scripts\\python.exe docs\\assets\\fable-5-2\\src\\mcp_diagram.py
Writes: docs/assets/fable-5-2/mcp.png
"""

from __future__ import annotations

import json
from pathlib import Path

from mythos import mcp_server
from mythos.service import Job

import style as S
from diagram import Canvas, text_width

RECORDS = json.loads(
    (Path(__file__).resolve().parent / "data" / "job_records.json").read_text(encoding="utf-8"))

# One line per tool, from each tool's docstring in src/mythos/mcp_server.py.
TOOLS = [
    ("m2m_create_animation", "Start a run. Returns the job record at once."),
    ("m2m_get_job", "Poll one job by id."),
    ("m2m_list_runs", "List the runs on disk, newest first."),
    ("m2m_get_run", "Manifest and file list for one run."),
    ("m2m_get_artifact", "Read one file from a run."),
    ("m2m_get_scene_code", "Read the generated scene, mythos_scene.py."),
    ("m2m_cinematic_charter", "Return the Cinematic Charter text."),
]
KEY_FIELDS = ("status", "stage", "outcome")


def record_lines(record: dict) -> list[tuple[str, bool]]:
    """The job record as JSON lines; the manifest body is elided."""
    lines: list[tuple[str, bool]] = [("{", False)]
    keys = list(record)
    for i, key in enumerate(keys):
        comma = "," if i < len(keys) - 1 else ""
        value = record[key]
        if key == "manifest":
            text = "{ ... }" if value else "null"
        elif key == "options":
            items = [f'"{k}": {json.dumps(v)}' for k, v in value.items()]
            lines.append((f'  "{key}": {{ {", ".join(items[:2])},', False))
            lines.append((f'    {", ".join(items[2:])} }}{comma}', False))
            continue
        else:
            text = json.dumps(value)
        lines.append((f'  "{key}": {text}{comma}', key in KEY_FIELDS))
    lines.append(("}", False))
    return lines


def main() -> None:
    for name, _ in TOOLS:
        assert callable(getattr(mcp_server, name)), name
    assert len(TOOLS) == 7
    running = RECORDS["running"]
    assert list(running) == list(Job(id="x", prompt="x").to_dict())
    assert len(running["options"]) == 4

    c = Canvas(height=1166)
    top = c.header(
        "How an agent uses it: the Mythos MCP server",
        "Commit 9e154fd, src/mythos/mcp_server.py. Every tool runs or reads the Mythos chain.",
        "NOW", S.OLIVE)
    panel_h = 946

    # ---------------- left: seven tools -----------------------------------
    lx, lw = S.MARGIN, 600
    y = c.panel(lx, top, lw, panel_h, "Seven tools", "Start the server with:")
    c.box(lx + 24, y, lw - 48, 52, fill=S.INK, outline=S.LINE)
    c.text(lx + 42, y + 26, "math-to-manim-mythos serve-mcp", "mono", S.LABEL, S.GOLD)
    y += 52 + 22
    row_h = 106
    for i, (name, note) in enumerate(TOOLS):
        ry = y + i * row_h
        if i:
            c.line([(lx + 24, ry), (lx + lw - 24, ry)], fill=S.LINE, width=1)
        c.text(lx + 24, ry + 38, name, "mono", S.LABEL, S.IVORY)
        assert text_width(note, "regular", S.NOTE) < lw - 48, note
        c.text(lx + 24, ry + 72, note, "regular", S.NOTE, S.FOG)

    # ---------------- right: the calls and one poll -----------------------
    rx = lx + lw + 24
    rw = c.width - S.MARGIN - rx
    y = c.panel(rx, top, rw, panel_h, "One job, start to finish",
                "The agent starts a run, polls the job, then reads the result.")
    steps = [("m2m_create_animation", "returns the job"),
             ("m2m_get_job", "repeat until done"),
             ("m2m_get_scene_code", "the scene file")]
    widths = [text_width(name, "mono", S.NOTE) + 28 for name, _ in steps]
    gap = (rw - 48 - sum(widths)) / 2
    assert gap >= 34
    x = rx + 24
    for i, ((name, note), w) in enumerate(zip(steps, widths)):
        c.chip(x, y, name, S.FOG if i != 1 else S.CORAL)
        c.text(x + 14, y + 62, note, "regular", S.NOTE, S.FOG)
        if i < 2:
            c.arrow([(x + w + 6, y + 20), (x + w + gap - 6, y + 20)])
        x += w + gap
    y += 100

    c.text(rx + 24, y + 14, "One poll while the run is at its fourth stage",
           "bold", S.LABEL, S.IVORY)
    y += 44
    lines = record_lines(running)
    code_h = len(lines) * 31 + 28
    c.box(rx + 24, y, rw - 48, code_h, fill=S.INK, outline=S.LINE)
    for i, (line, strong) in enumerate(lines):
        mid = y + 14 + i * 31 + 15
        if strong:
            c.line([(rx + 38, mid - 12), (rx + 38, mid + 12)], fill=S.CORAL, width=3)
        assert text_width(line, "mono", S.NOTE) < rw - 48 - 44, line
        c.text(rx + 52, mid, line, "mono", S.NOTE, S.IVORY if strong else S.FOG)
    y += code_h + 30

    # ---------------- the three fields across three polls -----------------
    c.text(rx + 24, y + 12, "The three fields an agent reads", "bold", S.LABEL, S.IVORY)
    y += 44
    cols = [rx + 24, rx + 250, rx + 422, rx + 636]
    for x, head in zip(cols, ("poll", *KEY_FIELDS)):
        c.text(x, y + 14, head, "regular", S.NOTE, S.MUTED)
    y += 34
    table = [("while running", RECORDS["running"]),
             ("offline run done", RECORDS["completed"]),
             ("backend failed", RECORDS["failed"])]
    for label, rec in table:
        c.line([(rx + 24, y), (rx + rw - 24, y)], fill=S.LINE, width=1)
        c.text(cols[0], y + 22, label, "regular", S.NOTE, S.FOG)
        for x, key in zip(cols[1:], KEY_FIELDS):
            value = rec[key]
            good = value in ("completed", "scene_ready")
            bad = value in ("failed", "chain_failed")
            fill = S.OLIVE if good else S.CORAL if bad else S.IVORY
            cell = json.dumps(value)
            assert x + text_width(cell, "mono", S.NOTE) < rx + rw - 24, cell
            c.text(x, y + 22, cell, "mono", S.NOTE, fill if value is not None else S.MUTED)
        y += 44
    assert y < top + panel_h - 10, y

    c.save("mcp.png")


if __name__ == "__main__":
    main()
