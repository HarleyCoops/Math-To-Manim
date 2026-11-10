"""Render one shot of a SceneSpec with one engine, and compare engines.

    render_shot(spec_path, "lattice", engine="blender")
    compare_engines(spec_path, "lattice", ["manim", "blender"])

Each render writes ``<runs>/shots/<shot>/<engine>/shot.png`` beside the
compiled shot it was made from. ``compare_engines`` also writes a side-by-side
image and a 50% blend, so a camera mismatch between engines is visible.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from studio.doctor import Runner, run_command
from studio.settings import BLENDER_GPU_BACKEND, default_runs_dir, find_blender
from studio.spec.compile import compile_shot
from studio.spec.models import load_spec

ENGINES_DIR = Path(__file__).resolve().parent / "engines"
SRC_DIR = Path(__file__).resolve().parents[1]
RENDERABLE = ("manim", "blender")


def _manim_scene_file(compiled_path: Path) -> str:
    return (
        "import sys\n"
        f"sys.path.insert(0, {str(SRC_DIR)!r})\n"
        "from studio.engines.manim_shot import build_scene\n"
        # Manim lists only the scenes that are defined in the file it is given.
        f"class StudioShot(build_scene({str(compiled_path)!r})):\n"
        "    pass\n"
    )


def render_shot(spec_path: Path | str, shot_id: str, *, engine: str | None = None,
                out_root: Path | None = None, samples: int = 64,
                runner: Runner = run_command) -> dict[str, Any]:
    """Render ``shot_id`` and return ``{ok, engine, image, seconds, detail}``."""
    spec = load_spec(spec_path)
    engine = engine or spec.shot(shot_id).engine
    if engine not in RENDERABLE:
        raise ValueError(f"engine {engine!r} cannot be rendered yet; "
                         f"choose one of: {', '.join(RENDERABLE)}")
    compiled = compile_shot(spec, shot_id)
    out_dir = (out_root or default_runs_dir() / "shots") / shot_id / engine
    out_dir.mkdir(parents=True, exist_ok=True)
    compiled_path = out_dir / "compiled.json"
    compiled_path.write_text(json.dumps(compiled, indent=2), encoding="utf-8")
    image = out_dir / "shot.png"
    image.unlink(missing_ok=True)

    started = time.perf_counter()
    if engine == "blender":
        blender = find_blender()
        if blender is None:
            return {"ok": False, "engine": engine, "detail": "blender not found"}
        code, output = runner([
            str(blender), "--background", "--factory-startup",
            "--gpu-backend", BLENDER_GPU_BACKEND,
            "--python", str(ENGINES_DIR / "blender_shot.py"),
            "--", str(compiled_path), str(image), str(samples)], 1800.0)
    else:
        scene_file = out_dir / "shot_scene.py"
        scene_file.write_text(_manim_scene_file(compiled_path), encoding="utf-8")
        media = out_dir / "media"
        code, output = runner([
            sys.executable, "-m", "manim", "-s", "--disable_caching",
            "--resolution", f"{compiled['width']},{compiled['height']}",
            "--media_dir", str(media), str(scene_file), "StudioShot"], 1800.0)
        stills = sorted(media.rglob("StudioShot*.png"))
        if code == 0 and stills:
            image.write_bytes(stills[-1].read_bytes())
    seconds = round(time.perf_counter() - started, 3)
    if code != 0 or not image.is_file():
        return {"ok": False, "engine": engine, "exit_code": code, "seconds": seconds,
                "detail": output[-2000:]}
    return {"ok": True, "engine": engine, "image": str(image), "seconds": seconds,
            "compiled": str(compiled_path)}


def compare_engines(spec_path: Path | str, shot_id: str, engines: list[str], *,
                    out_root: Path | None = None, runner: Runner = run_command
                    ) -> dict[str, Any]:
    """Render the same shot with several engines and write comparison images."""
    from PIL import Image

    results = [render_shot(spec_path, shot_id, engine=engine, out_root=out_root,
                           runner=runner) for engine in engines]
    report: dict[str, Any] = {"shot": shot_id, "renders": results, "ok": False}
    if not all(r["ok"] for r in results):
        return report
    images = [Image.open(r["image"]).convert("RGB") for r in results]
    width, height = images[0].size
    images = [im if im.size == (width, height) else im.resize((width, height))
              for im in images]
    out_dir = (out_root or default_runs_dir() / "shots") / shot_id
    side = Image.new("RGB", (width * len(images), height))
    for index, im in enumerate(images):
        side.paste(im, (index * width, 0))
    side_path = out_dir / f"compare_{'_'.join(engines)}.png"
    side.save(side_path)
    blend_path = out_dir / f"blend_{'_'.join(engines)}.png"
    Image.blend(images[0], images[1], 0.5).save(blend_path)
    report.update(ok=True, side_by_side=str(side_path), blend=str(blend_path))
    return report
