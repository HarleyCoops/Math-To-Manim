"""studio-engines.png: one SceneSpec shot rendered by Manim and by Blender.

The two pictures come from ``math-to-manim-studio compare`` on
``src/studio/examples/lattice.json``. Both engines draw the same compiled
shot from the same camera, so the atoms land on the same pixels.

Usage:  set PYTHONPATH=src
        .venv\\Scripts\\python.exe -m studio.cli compare src\\studio\\examples\\lattice.json --shot lattice
        .venv\\Scripts\\python.exe docs\\assets\\fable-5-2\\src\\studio_engines.py
Writes: docs/assets/fable-5-2/studio-engines.png  (1600 x 530)
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
SHOTS = ROOT / "runs" / "studio" / "shots" / "lattice"
OUT = Path(__file__).resolve().parents[1] / "studio-engines.png"
PAPER, IVORY, MUTED = "#0c0c0b", "#faf9f5", "#a8a69d"
PANEL_W, PANEL_H, STRIP = 800, 450, 80


def font(size: int) -> ImageFont.ImageFont:
    for name in ("Poppins-Medium.ttf", "segoeui.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> None:
    panels = [("Manim", "Cairo renderer", SHOTS / "manim" / "shot.png"),
              ("Blender", "EEVEE, OpenGL backend", SHOTS / "blender" / "shot.png")]
    sheet = Image.new("RGB", (PANEL_W * 2, PANEL_H + STRIP), PAPER)
    draw = ImageDraw.Draw(sheet)
    for index, (name, note, path) in enumerate(panels):
        picture = Image.open(path).convert("RGB").resize((PANEL_W, PANEL_H), Image.LANCZOS)
        x = index * PANEL_W
        sheet.paste(picture, (x, 0))
        draw.text((x + 40, PANEL_H + 12), name, font=font(28), fill=IVORY)
        draw.text((x + 40, PANEL_H + 48), note, font=font(19), fill=MUTED)
    draw.line([(PANEL_W, 24), (PANEL_W, PANEL_H + STRIP - 24)], fill="#3d3d3a", width=2)
    sheet.save(OUT, optimize=True)
    print(f"wrote {OUT} {sheet.size}")


main()
