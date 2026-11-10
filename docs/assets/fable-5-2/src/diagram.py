"""Small Pillow drawing kit shared by the README diagrams.

Coordinates and sizes are in pixels of the final image. Everything is drawn
at 2x and downsampled once, so edges and text are antialiased.
"""

from __future__ import annotations

import math
import sys
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import style as S  # noqa: E402

SS = 2  # supersampling factor

_FONTS = {"bold": S.FONT_BOLD, "regular": S.FONT_REGULAR,
          "italic": S.FONT_ITALIC, "mono": S.FONT_MONO}


@lru_cache(maxsize=None)
def _font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(_FONTS[kind], size * SS)


def text_width(text: str, kind: str = "regular", size: int = S.LABEL) -> float:
    return _font(kind, size).getlength(text) / SS


class Canvas:
    def __init__(self, height: int, width: int = S.WIDTH, background: str = S.INK):
        self.width, self.height = width, height
        self.image = Image.new("RGB", (width * SS, height * SS), background)
        self.draw = ImageDraw.Draw(self.image)

    # -- text -------------------------------------------------------------
    def text(self, x: float, y: float, text: str, kind: str = "regular",
             size: int = S.LABEL, fill: str = S.IVORY, anchor: str = "lm") -> float:
        """Draw one line. ``anchor`` is a Pillow anchor; default left-middle."""
        self.draw.text((x * SS, y * SS), text, font=_font(kind, size), fill=fill,
                       anchor=anchor)
        return text_width(text, kind, size)

    def runs(self, x: float, y: float, parts: list[tuple], anchor_right: bool = False) -> float:
        """Draw runs ``(text, kind, size, fill)`` on one baseline row; return width."""
        total = sum(text_width(t, k, s) for t, k, s, _ in parts)
        cursor = x - total if anchor_right else x
        for t, k, s, fill in parts:
            self.text(cursor, y, t, k, s, fill)
            cursor += text_width(t, k, s)
        return total

    # -- shapes -----------------------------------------------------------
    def box(self, x: float, y: float, w: float, h: float, fill: str | None = S.PANEL,
            outline: str | None = S.LINE, dashed: bool = False,
            radius: int = S.RADIUS, width: int = S.STROKE) -> None:
        xy = [x * SS, y * SS, (x + w) * SS, (y + h) * SS]
        if dashed:
            if fill:
                self.draw.rounded_rectangle(xy, radius=radius * SS, fill=fill)
            if outline:
                self.dashes(_rounded_path(x, y, w, h, radius), outline, width)
        else:
            self.draw.rounded_rectangle(xy, radius=radius * SS, fill=fill,
                                        outline=outline, width=width * SS)

    def line(self, points: list[tuple[float, float]], fill: str = S.FOG,
             width: int = S.STROKE, dashed: bool = False) -> None:
        if dashed:
            self.dashes(points, fill, width)
            return
        self.draw.line([(px * SS, py * SS) for px, py in points], fill=fill,
                       width=width * SS, joint="curve")

    def dashes(self, points: list[tuple[float, float]], fill: str, width: int = S.STROKE,
               dash: float = 9, gap: float = 7) -> None:
        """Dashed polyline: the mark for anything planned and not built."""
        pos, drawing = 0.0, True
        remaining = dash
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            length = math.hypot(x1 - x0, y1 - y0)
            if length == 0:
                continue
            ux, uy = (x1 - x0) / length, (y1 - y0) / length
            pos = 0.0
            while pos < length:
                step = min(remaining, length - pos)
                if drawing:
                    self.draw.line(
                        [((x0 + ux * pos) * SS, (y0 + uy * pos) * SS),
                         ((x0 + ux * (pos + step)) * SS, (y0 + uy * (pos + step)) * SS)],
                        fill=fill, width=width * SS)
                pos += step
                remaining -= step
                if remaining <= 1e-6:
                    drawing = not drawing
                    remaining = dash if drawing else gap

    def arrow(self, points: list[tuple[float, float]], fill: str = S.FOG,
              dashed: bool = False, head: float = 11) -> None:
        """Polyline with one arrowhead at the last point."""
        (x0, y0), (x1, y1) = points[-2], points[-1]
        length = math.hypot(x1 - x0, y1 - y0) or 1.0
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        base = (x1 - ux * head, y1 - uy * head)
        self.line([*points[:-1], (x1 - ux * head * 0.8, y1 - uy * head * 0.8)],
                  fill=fill, dashed=dashed)
        half = head * 0.55
        tri = [(x1, y1), (base[0] - uy * half, base[1] + ux * half),
               (base[0] + uy * half, base[1] - ux * half)]
        self.draw.polygon([(px * SS, py * SS) for px, py in tri], fill=fill)

    def dot(self, x: float, y: float, r: float, fill: str) -> None:
        self.draw.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=fill)

    def ring(self, x: float, y: float, r: float, outline: str, fill: str | None = None) -> None:
        self.draw.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS],
                          outline=outline, fill=fill, width=S.STROKE * SS)

    # -- compound pieces --------------------------------------------------
    def chip(self, x: float, y: float, text: str, color: str = S.FOG, kind: str = "mono",
             size: int = S.NOTE, h: float = 40, fill: str | None = S.PANEL_HI,
             dashed: bool = False, text_fill: str | None = None, pad: float = 14) -> float:
        """Rounded label with its top-left at (x, y); returns its width."""
        w = text_width(text, kind, size) + 2 * pad
        self.box(x, y, w, h, fill=fill, outline=color, dashed=dashed)
        self.text(x + pad, y + h / 2, text, kind, size, text_fill or S.IVORY)
        return w

    def header(self, title: str, note: str, tag: str, tag_color: str,
               tag_dashed: bool = False) -> float:
        """Image title, one note line and a state tag. Returns the content top."""
        self.line([(S.MARGIN, 64), (S.MARGIN + 44, 64)], fill=S.CORAL, width=4)
        self.text(S.MARGIN + 62, 64, title, "bold", S.TITLE, S.IVORY)
        self.text(S.MARGIN, 122, note, "regular", S.NOTE, S.FOG)
        w = text_width(tag, "bold", S.NOTE) + 36
        self.box(self.width - S.MARGIN - w, 42, w, 44, fill=None, outline=tag_color,
                 dashed=tag_dashed)
        self.text(self.width - S.MARGIN - w / 2, 64, tag, "bold", S.NOTE, tag_color, "mm")
        return 164

    def panel(self, x: float, y: float, w: float, h: float, title: str,
              note: str | None = None, dashed: bool = False) -> float:
        """Panel with a title row. Returns the y where its content starts."""
        self.box(x, y, w, h, fill=S.PANEL, outline=S.LINE, dashed=dashed)
        self.text(x + 24, y + 38, title, "bold", S.LABEL, S.IVORY)
        if note:
            self.text(x + 24, y + 74, note, "regular", S.NOTE, S.FOG)
            return y + 104
        return y + 72

    def code(self, x: float, y: float, lines: list[tuple[str, str]], size: int = S.NOTE,
             leading: float = 31) -> float:
        """Mono lines ``(text, fill)``; returns the y after the last line."""
        for index, (line, fill) in enumerate(lines):
            self.text(x, y + index * leading + leading / 2, line, "mono", size, fill)
        return y + len(lines) * leading

    def save(self, name: str, colors: int | None = None) -> Path:
        """Downsample and write. ``colors`` writes a palette PNG (smaller file)."""
        out = S.OUT_DIR / name
        final = self.image.resize((self.width, self.height), Image.LANCZOS)
        if colors:
            final = final.quantize(colors=colors, method=Image.Quantize.MEDIANCUT,
                                   dither=Image.Dither.NONE)
        final.save(out, optimize=True)
        print(out, final.size, out.stat().st_size)
        return out


def _rounded_path(x: float, y: float, w: float, h: float, r: float) -> list[tuple[float, float]]:
    """Closed outline of a rounded rectangle as a polyline."""
    points: list[tuple[float, float]] = []
    corners = [(x + w - r, y + r, -90), (x + w - r, y + h - r, 0),
               (x + r, y + h - r, 90), (x + r, y + r, 180)]
    for cx, cy, start in corners:
        for step in range(0, 7):
            angle = math.radians(start + step * 15)
            points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    points.append(points[0])
    return points
