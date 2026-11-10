"""studio-planned.png: the planned Studio pipeline. Planned, not built.

Nothing here is read from the repo: Studio is a design approved in outline
and has no code in ``src/``. Every box is drawn with a dashed outline, the
mark this image set uses for "planned".

Usage:  .venv\\Scripts\\python.exe docs\\assets\\fable-5-2\\src\\studio_planned.py
Writes: docs/assets/fable-5-2/studio-planned.png
"""

from __future__ import annotations

import style as S
from diagram import Canvas, text_width

AGENTS = ["Story Scout", "Physics Verifier", "Director",
          "Spec Author", "Manim Builder", "Blender Builder",
          "Web Builder", "Visual Critic", "Fact Checker"]
MAX_ROUNDS = 3


def main() -> None:
    assert len(AGENTS) == 9
    c = Canvas(height=1112)
    top = c.header(
        "What comes next: Studio",
        "A design approved in outline. None of this is in src/ yet. "
        "Dashed outlines mean planned.",
        "PLANNED, NOT BUILT", S.GOLD, tag_dashed=True)

    def card(x, y, w, h, name, notes=(), outline=S.FOG, mono=False):
        c.box(x, y, w, h, fill=S.PANEL_HI, outline=outline, dashed=True)
        c.text(x + 18, y + 32, name, "mono" if mono else "bold", S.LABEL, S.IVORY)
        for i, line in enumerate(notes):
            assert text_width(line, "regular", S.NOTE) < w - 30, line
            c.text(x + 18, y + 68 + i * 30, line, "regular", S.NOTE, S.FOG)

    # ---------------- row 1: agents -> SceneSpec -> engines -> outputs ----
    row_h = 420
    ax, aw = S.MARGIN, 470
    y = c.panel(ax, top, aw, row_h, "Nine agents",
                "Each agent writes one typed file.", dashed=True)
    cell_w, cell_h = (aw - 48 - 12) / 2, 50
    for i, name in enumerate(AGENTS):
        col, row = i % 2, i // 2
        x = ax + 24 + col * (cell_w + 12)
        yy = y + row * (cell_h + 12)
        c.box(x, yy, cell_w, cell_h, fill=S.PANEL_HI, outline=S.LINE, dashed=True)
        assert text_width(name, "regular", S.NOTE) < cell_w - 24, name
        c.text(x + 14, yy + cell_h / 2, name, "regular", S.NOTE, S.IVORY)

    mid = top + row_h / 2
    sx, sw, sh = ax + aw + 56, 250, 170
    card(sx, mid - sh / 2, sw, sh, "SceneSpec",
         ["one typed scene", "description", "for all three engines"], outline=S.GOLD, mono=True)
    c.arrow([(ax + aw, mid), (sx, mid)], dashed=True)

    ex, ew, eh = sx + sw + 56, 290, 112
    engine_y = [top + 14, top + 14 + eh + 28, top + 14 + 2 * (eh + 28)]
    card(ex, engine_y[0], ew, eh, "Manim", ["shots for the film"], outline=S.CORAL)
    card(ex, engine_y[1], ew, eh, "Blender", ["EEVEE, on the user's PC"], outline=S.SKY)
    card(ex, engine_y[2], ew, eh, "three.js", ["the interactive page"], outline=S.OLIVE)
    fork = sx + sw + 28
    for ey in engine_y:
        c.arrow([(sx + sw, mid), (fork, mid), (fork, ey + eh / 2), (ex, ey + eh / 2)],
                dashed=True)

    ox = ex + ew + 56
    ow = c.width - S.MARGIN - ox
    film_y = (engine_y[0] + engine_y[1]) / 2
    card(ox, film_y, ow, eh, "MP4 film", ["Manim and Blender shots"], outline=S.IVORY)
    card(ox, engine_y[2], ow, eh, "Web page", ["interactive, three.js"], outline=S.IVORY)
    join = ex + ew + 28
    for ey in engine_y[:2]:
        c.arrow([(ex + ew, ey + eh / 2), (join, ey + eh / 2), (join, film_y + eh / 2),
                 (ox, film_y + eh / 2)], dashed=True)
    c.arrow([(ex + ew, engine_y[2] + eh / 2), (ox, engine_y[2] + eh / 2)], dashed=True)

    # ---------------- row 2: the per-shot loop ------------------------------
    ly = top + row_h + 24
    lh = 300
    y = c.panel(S.MARGIN, ly, c.width - 2 * S.MARGIN, lh, "For each shot",
                "The run is a state machine in code, with one state per shot.", dashed=True)
    names = [("build", ["an engine renders", "the shot"]),
             ("measure", ["code measures", "the render"]),
             ("review", ["a critic looks at", "a contact sheet"]),
             ("shot done", ["go to the", "next shot"])]
    bw, bh = 286, 124
    inner = c.width - 2 * S.MARGIN - 48
    gap = (inner - 4 * bw) / 3
    xs = [S.MARGIN + 24 + i * (bw + gap) for i in range(4)]
    for x, (name, notes) in zip(xs, names):
        card(x, y, bw, bh, name, notes,
             outline=S.OLIVE if name == "shot done" else S.FOG)
    for a, b in zip(xs, xs[1:]):
        c.arrow([(a + bw, y + 46), (b, y + 46)], dashed=True)
    c.text((xs[2] + bw + xs[3]) / 2, y + 26, "pass", "regular", S.NOTE, S.OLIVE, "mm")
    # repair: from review back to build, under the row
    back_y = y + bh + 36
    c.arrow([(xs[2] + bw / 2, y + bh), (xs[2] + bw / 2, back_y), (xs[0] + bw / 2, back_y),
             (xs[0] + bw / 2, y + bh)], fill=S.CORAL, dashed=True)
    label = f"repair, at most {MAX_ROUNDS} rounds"
    lw_ = text_width(label, "regular", S.NOTE)
    cx = (xs[0] + bw + xs[2]) / 2
    c.box(cx - lw_ / 2 - 12, back_y - 18, lw_ + 24, 36, fill=S.PANEL, outline=None)
    c.text(cx, back_y, label, "regular", S.NOTE, S.CORAL, "mm")

    # ---------------- row 3: where it runs ----------------------------------
    ny = ly + lh + 24
    nh = 124
    third = (c.width - 2 * S.MARGIN - 24) / 2
    notes = [("Where the agents run", ["Claude Managed Agents"]),
             ("Run viewer", ["shows a run while it runs"])]
    for i, (name, lines) in enumerate(notes):
        x = S.MARGIN + i * (third + 24)
        c.box(x, ny, third, nh, fill=S.PANEL, outline=S.LINE, dashed=True)
        c.text(x + 24, ny + 38, name, "bold", S.LABEL, S.IVORY)
        for j, line in enumerate(lines):
            c.text(x + 24, ny + 76 + j * 30, line, "regular", S.NOTE, S.FOG)
    assert ny + nh + S.MARGIN <= c.height, ny + nh + S.MARGIN

    c.save("studio-planned.png")


if __name__ == "__main__":
    main()
