"""contact-sheet.png: the five README images on one sheet, for review.

Usage:  .venv\\Scripts\\python.exe docs\\assets\\fable-5-2\\src\\contact_sheet.py
Writes: docs/assets/fable-5-2/contact-sheet.png
"""

from __future__ import annotations

from PIL import Image

import style as S
from diagram import SS, Canvas

IMAGES = [
    ("hero.png", "Title image. A Manim CE ThreeDScene still."),
    ("chain.png", "How the chain works now."),
    ("lifecycle.png", "What changed: job and run lifecycles."),
    ("mcp.png", "How an agent uses the MCP server."),
    ("studio-planned.png", "Planned: the Studio pipeline."),
]


def main() -> None:
    gap = 24
    cell_w = (S.WIDTH - 2 * S.MARGIN - gap) // 2
    label_h = 78
    loaded = [(name, note, Image.open(S.OUT_DIR / name).convert("RGB"))
              for name, note in IMAGES]
    hero = loaded[0]
    rest = loaded[1:]
    hero_w = S.WIDTH - 2 * S.MARGIN
    hero_h = round(hero[2].height * hero_w / hero[2].width)
    heights = [round(img.height * cell_w / img.width) for _, _, img in rest]
    row_heights = [max(heights[0:2]), max(heights[2:4])]
    top = 164
    total = top + hero_h + label_h + sum(h + label_h for h in row_heights) + S.MARGIN - 20

    c = Canvas(height=total)
    c.header("Fable 5.2 Learns Manim: the image set",
             "The five images for the README section, scaled down.",
             "REVIEW SHEET", S.FOG)

    def place(image: Image.Image, x: int, y: int, w: int, h: int, name: str, note: str,
              index: int) -> None:
        thumb = image.resize((w * SS, h * SS), Image.LANCZOS)
        c.image.paste(thumb, (x * SS, y * SS))
        c.box(x, y, w, h, fill=None, outline=S.LINE, radius=0)
        c.runs(x, y + h + 26, [(f"{index}  ", "bold", S.NOTE, S.CORAL),
                               (name, "mono", S.NOTE, S.IVORY),
                               (f"   {image.width} x {image.height}", "regular", S.NOTE, S.MUTED)])
        c.text(x, y + h + 54, note, "regular", S.NOTE, S.FOG)

    y = top
    place(hero[2], S.MARGIN, y, hero_w, hero_h, hero[0], hero[1], 1)
    y += hero_h + label_h
    for row in range(2):
        for col in range(2):
            name, note, image = rest[row * 2 + col]
            x = S.MARGIN + col * (cell_w + gap)
            place(image, x, y, cell_w, heights[row * 2 + col], name, note, row * 2 + col + 2)
        y += row_heights[row] + label_h

    c.save("contact-sheet.png", colors=256)  # palette PNG keeps the sheet under 1 MB


if __name__ == "__main__":
    main()
