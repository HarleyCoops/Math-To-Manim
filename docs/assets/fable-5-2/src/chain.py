"""chain.png: how the Mythos chain works now.

Stage names and file names are read from ``mythos.stages.STAGES`` and
``mythos.layout``; nothing is typed in by hand.

Usage:  .venv\\Scripts\\python.exe docs\\assets\\fable-5-2\\src\\chain.py
Writes: docs/assets/fable-5-2/chain.png
"""

from __future__ import annotations

import inspect

from mythos.harness import MythosHarness
from mythos.layout import MANIFEST_FILE, SCENE_FILE, VALIDATION_FILE
from mythos.stages import STAGES

import style as S
from diagram import Canvas, text_width

MAX_REPAIRS = inspect.signature(MythosHarness.run).parameters["max_repairs"].default


def main() -> None:
    assert len(STAGES) == 6
    c = Canvas(height=968)
    top = c.header(
        "The Mythos chain today",
        "src/mythos/stages.py and src/mythos/harness.py. Each step writes one file "
        "into the run directory.",
        "NOW", S.OLIVE)

    # ---------------- left: six reasoning stages -------------------------
    lx, lw = S.MARGIN, 784
    panel_h = 748
    y = c.panel(lx, top, lw, panel_h, "Six reasoning stages",
                "Each stage reads the file before it and writes one JSON file.")
    row_h, row_gap = 78, 14
    cx = lx + 62
    centers = []
    for index, stage in enumerate(STAGES):
        ry = y + index * (row_h + row_gap)
        c.box(lx + 24, ry, lw - 48, row_h, fill=S.PANEL_HI, outline=S.LINE)
        mid = ry + row_h / 2
        centers.append(mid)
        c.ring(cx, mid, 17, S.CORAL, fill=S.PANEL_HI)
        c.text(cx, mid, str(index + 1), "bold", S.NOTE, S.CORAL, "mm")
        c.text(lx + 100, mid, stage.slug, "mono", S.LABEL, S.IVORY)
        c.arrow([(lx + 352, mid), (lx + 392, mid)], fill=S.MUTED, head=9)
        c.text(lx + 408, mid, stage.artifact, "mono", S.LABEL, S.GOLD)
        assert lx + 408 + text_width(stage.artifact, "mono", S.LABEL) < lx + lw - 40
    for a, b in zip(centers, centers[1:]):
        c.arrow([(cx, a + 19), (cx, b - 19)], fill=S.CORAL, head=9)
    note_y = y + 6 * (row_h + row_gap) + 14
    c.text(lx + 24, note_y + 10, "A reply that fails its size or list check is retried once.",
           "regular", S.NOTE, S.FOG)
    c.text(lx + 24, note_y + 42, "A second failure stops the run.", "regular", S.NOTE, S.FOG)

    # ---------------- right: build and check -----------------------------
    rx = lx + lw + 24
    rw = c.width - S.MARGIN - rx
    y = c.panel(rx, top, rw, panel_h, "Build and check",
                "The model writes the scene. Code checks it and renders it.")
    bx, bw, bh = rx + 24, 330, 122
    px, pw = rx + rw - 24 - 208, 208
    y_code, y_verify, y_render = y, y + 160, y + 320
    y_end = y + 480

    def step(x, yy, w, h, name, lines, name_color=S.IVORY):
        c.box(x, yy, w, h, fill=S.PANEL_HI, outline=S.LINE)
        c.text(x + 18, yy + 30, name, "mono", S.LABEL, name_color)
        for i, parts in enumerate(lines):
            assert c.runs(x + 18, yy + 66 + i * 30, parts) < w - 34, parts

    note = lambda t: (t, "regular", S.NOTE, S.FOG)          # noqa: E731
    file = lambda t: (t, "mono", S.NOTE, S.GOLD)            # noqa: E731

    step(bx, y_code, bw, bh, "codegen",
         [[note("reads the six files")], [note("writes "), file(SCENE_FILE)]])
    step(bx, y_verify, bw, bh, "verify",
         [[note("checks AST, LaTeX, Charter")], [note("writes "), file(VALIDATION_FILE)]])
    step(bx, y_render, bw, bh, "render",
         [[note("runs manim (with --render)")], [note("writes "), file("render_N.log")]])
    # repair spans the verify and render rows
    c.box(px, y_verify, pw, y_render + bh - y_verify, fill=S.PANEL_HI, outline=S.CORAL)
    c.text(px + 18, y_verify + 30, "repair", "mono", S.LABEL, S.IVORY)
    for i, line in enumerate(("The model", "rewrites the", "scene file.", "",
                              f"At most {MAX_REPAIRS} rounds", "by default",
                              "(--max-repairs).")):
        c.text(px + 18, y_verify + 66 + i * 30, line, "regular", S.NOTE, S.FOG)

    mid_x = bx + bw / 2
    # all six files go to codegen
    c.arrow([(lx + lw, y_code + bh / 2), (bx, y_code + bh / 2)], fill=S.CORAL)
    c.arrow([(mid_x, y_code + bh), (mid_x, y_verify)])
    c.arrow([(mid_x, y_verify + bh), (mid_x, y_render)])
    c.text(mid_x + 14, (y_verify + bh + y_render) / 2, "passed", "regular", S.NOTE, S.FOG)
    gap_mid = (bx + bw + px) / 2
    # verify -> repair, repair -> verify
    c.arrow([(bx + bw, y_verify + 40), (px, y_verify + 40)], fill=S.CORAL)
    c.text(gap_mid, y_verify + 20, "failed", "regular", S.NOTE, S.CORAL, "mm")
    c.arrow([(px, y_verify + 88), (bx + bw, y_verify + 88)])
    c.text(gap_mid, y_verify + 108, "new file", "regular", S.NOTE, S.FOG, "mm")
    # render -> repair
    c.arrow([(bx + bw, y_render + 61), (px, y_render + 61)], fill=S.CORAL)
    c.text(gap_mid, y_render + 41, "failed", "regular", S.NOTE, S.CORAL, "mm")

    # the run ends
    end_w = rw - 48
    c.box(bx, y_end, end_w, 130, fill=S.PANEL_HI, outline=S.OLIVE)
    c.text(bx + 18, y_end + 30, "run ends", "regular", S.LABEL, S.IVORY)
    c.runs(bx + 18, y_end + 66, [file(MANIFEST_FILE), note(" records how it ended:")])
    c.runs(bx + 18, y_end + 98, [("status.run", "mono", S.NOTE, S.IVORY), note(", "),
                                 ("status.outcome", "mono", S.NOTE, S.IVORY)])
    c.arrow([(mid_x, y_render + bh), (mid_x, y_end)])
    c.text(mid_x + 14, (y_render + bh + y_end) / 2, "rendered", "regular", S.NOTE, S.FOG)
    rep_x = px + pw / 2
    c.arrow([(rep_x, y_render + bh), (rep_x, y_end)], fill=S.CORAL)
    label = "no rounds left"
    c.text(rep_x - 14, (y_render + bh + y_end) / 2, label, "regular", S.NOTE, S.CORAL, "rm")
    assert text_width(label, "regular", S.NOTE) < rep_x - 14 - (mid_x + 14 + 100)

    c.save("chain.png")


if __name__ == "__main__":
    main()
