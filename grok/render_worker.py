"""Host-owned render entry. Delivery settings override scene-level defaults.

Manim is imported inside main so the offline package can import without a
Manim install. Profiles are local so this file runs as a script without
putting the repository root on sys.path.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

PROFILES = {
    "l": (854, 480, 15),
    "m": (1280, 720, 30),
    "h": (1920, 1080, 60),
    "p": (2560, 1440, 60),
    "k": (3840, 2160, 60),
}


def main(source, media_dir, quality, mode="movie", scene_name=""):
    # Manim is optional. Importing it at module level would break offline use.
    from manim import tempconfig

    if quality not in PROFILES:
        raise SystemExit(f"unsupported quality: {quality}")
    if not scene_name:
        raise SystemExit("scene name is required")
    namespace = runpy.run_path(str(Path(source).resolve()))
    scene_class = namespace[scene_name]
    width, height, fps = PROFILES[quality]
    with tempconfig(
        {
            "pixel_width": width,
            "pixel_height": height,
            "frame_rate": fps,
            "renderer": "cairo",
            "media_dir": str(Path(media_dir).resolve()),
            "output_file": scene_name,
            "write_to_movie": mode == "movie",
            "save_last_frame": mode == "still",
            "disable_caching": True,
            "progress_bar": "none",
        }
    ):
        scene_class().render()


if __name__ == "__main__":
    main(*sys.argv[1:])
