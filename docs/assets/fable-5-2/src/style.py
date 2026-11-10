"""One visual system for the "Fable 5.2 Learns Manim" README images.

Palette: the Mythos house palette, copied from ``src/mythos/cinematography.py``
(INK, IVORY, CORAL, SKY, OLIVE, FOG, GOLD, EMBER). Two extra neutrals are
derived from INK and FOG for panels and hairlines.

Type: Poppins (titles and labels), Cascadia Mono (names that exist in code),
Lora Italic (captions). Poppins and Lora are read from the per-user Windows
font folder; Segoe UI is the fallback.

All sizes are in pixels of the final image (1600 px wide).
"""

from __future__ import annotations

import os
from pathlib import Path

# --- palette (src/mythos/cinematography.py) --------------------------------
INK = "#0c0c0b"      # background
IVORY = "#faf9f5"    # primary text
CORAL = "#d97757"    # primary accent
SKY = "#6a9bcc"      # secondary accent
OLIVE = "#788c5d"    # tertiary accent
FOG = "#b0aea5"      # secondary text
GOLD = "#d4a27f"     # emphasis
EMBER = "#bd5d3a"    # deep accent
# --- derived neutrals -------------------------------------------------------
PANEL = "#171715"    # panel fill
PANEL_HI = "#1f1f1c" # raised fill (cards inside panels)
LINE = "#3a3935"     # hairlines and panel borders
MUTED = "#8a8880"    # tertiary text (still >= 4.5:1 on INK)

# --- geometry ---------------------------------------------------------------
WIDTH = 1600
MARGIN = 56
RADIUS = 14          # one corner radius
STROKE = 2           # one line weight
GAP = 16

# --- type sizes -------------------------------------------------------------
TITLE = 40           # image title
LABEL = 26           # labels: what a thing is
NOTE = 21            # notes: one line about it

_USER_FONTS = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Windows" / "Fonts"
_SYS_FONTS = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"


def _first(*candidates: Path) -> str:
    for path in candidates:
        if path.is_file():
            return str(path)
    raise FileNotFoundError(f"none of these fonts exist: {candidates}")


FONT_BOLD = _first(_USER_FONTS / "Poppins-Bold.ttf", _SYS_FONTS / "segoeuib.ttf")
FONT_REGULAR = _first(_USER_FONTS / "Poppins-Regular.ttf", _SYS_FONTS / "segoeui.ttf")
FONT_ITALIC = _first(_USER_FONTS / "Lora-Italic.ttf", _SYS_FONTS / "segoeuii.ttf")
FONT_MONO = _first(_SYS_FONTS / "CascadiaMono.ttf", _SYS_FONTS / "consola.ttf")

OUT_DIR = Path(__file__).resolve().parent.parent
