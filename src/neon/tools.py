"""First-class toolbelt for the Gemini 4 Neon Math-To-Manim pipeline.

Every tool returns a structured JSON-serializable dict so it works identically
inside a live ``google-genai`` function-calling loop, a ``gemini-api`` CLI
orchestrator, or an active Gemini 4 Neon operator session.
"""

from __future__ import annotations

import ast
import cmath
import json
import math
import operator
import shutil
import subprocess
from pathlib import Path
from typing import Any

import numpy as np

from neon.models import MANIFEST_FILE, PLAN_FILE, SCENE_FILE, TOOL_LOG_FILE, VALIDATION_FILE, NeonManifest, NeonPlan
from neon.settings import scrubbed_env

_BANNED_IMPORTS = {
    "os",
    "sys",
    "subprocess",
    "shutil",
    "socket",
    "urllib",
    "http",
    "requests",
    "httpx",
    "ctypes",
    "pathlib",
    "importlib",
}
_BANNED_CALLS = {"eval", "exec", "__import__", "open", "compile"}

_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_SAFE_NAMES: dict[str, Any] = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "exp": math.exp,
    "log": math.log,
    "log2": math.log2,
    "log10": math.log10,
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "len": len,
    "complex": complex,
    "float": float,
    "int": int,
    "math": math,
    "cmath": cmath,
    "np": np,
}


def _eval_node(node: ast.AST) -> Any:
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float, complex)):
        return node.value
    if isinstance(node, ast.Name) and node.id in _SAFE_NAMES:
        return _SAFE_NAMES[node.id]
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_eval_node(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.Attribute):
        base = _eval_node(node.value)
        if base in (np, math, cmath) and not node.attr.startswith("_"):
            return getattr(base, node.attr)
        if isinstance(base, (complex, np.ndarray)) and node.attr in ("real", "imag", "T", "size"):
            return getattr(base, node.attr)
        raise ValueError(f"disallowed attribute access: {node.attr}")
    if isinstance(node, ast.Call):
        func = _eval_node(node.func)
        args = [_eval_node(arg) for arg in node.args]
        kwargs = {kw.arg: _eval_node(kw.value) for kw in node.keywords if kw.arg}
        return func(*args, **kwargs)
    if isinstance(node, (ast.List, ast.Tuple)):
        return [_eval_node(elt) for elt in node.elts]
    raise ValueError(f"unsupported AST node in verify_math: {type(node).__name__}")


def verify_math(expression: str) -> dict[str, Any]:
    """Safely evaluate a real or complex mathematical expression using math/cmath/numpy."""
    expr = str(expression or "").strip()
    if not expr:
        return {"ok": False, "expression": expr, "error": "expression was empty"}
    try:
        tree = ast.parse(expr, mode="eval")
        val = _eval_node(tree)
        if isinstance(val, np.ndarray):
            out: Any = val.tolist()
        elif isinstance(val, (np.floating, np.integer)):
            out = val.item()
        elif isinstance(val, (complex, np.complexfloating)):
            out = {"real": float(val.real), "imag": float(val.imag), "abs": float(abs(val))}
        else:
            out = val
        return {"ok": True, "expression": expr, "value": out}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "expression": expr, "error": str(exc)}


def check_scene(source: str) -> dict[str, Any]:
    """Statically validate a Manim Community Edition ThreeDScene Python file."""
    text = str(source or "")
    if not text.strip():
        return {"passed": False, "scene_class": None, "errors": ["scene source is empty"], "warnings": []}

    errors: list[str] = []
    warnings: list[str] = []

    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return {
            "passed": False,
            "scene_class": None,
            "errors": [f"SyntaxError at line {exc.lineno}: {exc.msg}"],
            "warnings": [],
            "line_count": len(text.splitlines()),
        }

    scene_class: str | None = None
    has_construct = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top in _BANNED_IMPORTS:
                    errors.append(f"banned import: {alias.name}")
        elif isinstance(node, ast.ImportFrom) and node.module:
            top = node.module.split(".")[0]
            if top in _BANNED_IMPORTS:
                errors.append(f"banned import from: {node.module}")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in _BANNED_CALLS:
                errors.append(f"banned call: {node.func.id}()")
        elif isinstance(node, ast.ClassDef):
            base_names = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    base_names.append(base.id)
                elif isinstance(base, ast.Attribute):
                    base_names.append(base.attr)
            if "ThreeDScene" in base_names:
                scene_class = node.name
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "construct":
                        has_construct = True

    if scene_class is None:
        errors.append("no ThreeDScene subclass found")
    elif not has_construct:
        errors.append(f"class {scene_class} is missing construct(self)")

    if "set_camera_orientation" not in text and "move_camera" not in text:
        errors.append("ThreeDScene must configure 3D camera via set_camera_orientation or move_camera")

    if ("MathTex(" in text or "Tex(" in text) and "add_fixed_in_frame_mobjects" not in text:
        warnings.append("HUD text detected without add_fixed_in_frame_mobjects")

    return {
        "passed": len(errors) == 0,
        "scene_class": scene_class,
        "errors": errors,
        "warnings": warnings,
        "line_count": len(text.splitlines()),
    }


def _probe_video(mp4_path: Path) -> dict[str, Any]:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe or not mp4_path.is_file():
        return {}
    proc = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,r_frame_rate,duration",
            "-show_entries",
            "format=duration,size",
            "-of",
            "json",
            str(mp4_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return {}
    try:
        info = json.loads(proc.stdout)
        stream = (info.get("streams") or [{}])[0]
        fmt = info.get("format") or {}
        dur = float(fmt.get("duration") or stream.get("duration") or 0.0)
        w = int(stream.get("width") or 0)
        h = int(stream.get("height") or 0)
        return {
            "duration_seconds": round(dur, 2),
            "width": w,
            "height": h,
            "resolution": f"{w}x{h}" if w and h else None,
            "size_bytes": int(fmt.get("size") or mp4_path.stat().st_size),
        }
    except Exception:  # noqa: BLE001
        return {}


def _generate_contact_sheet_and_gif(mp4_path: Path, run_dir: Path, duration: float) -> tuple[Path | None, Path | None]:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg or not mp4_path.is_file():
        return None, None

    contact_sheet = run_dir / "contact-sheet.png"
    fps_sample = max(0.05, 12.0 / max(duration, 1.0))
    cs_proc = subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(mp4_path),
            "-vf",
            f"fps={fps_sample:.4f},scale=426:-1,tile=4x3",
            "-frames:v",
            "1",
            str(contact_sheet),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    cs_out = contact_sheet if cs_proc.returncode == 0 and contact_sheet.is_file() else None

    gif_path = run_dir / "highlights.gif"
    palette_path = run_dir / "_palette.png"
    # Speed up slightly if film > 35s so the showcase GIF is punchy and compact
    speed = max(1.0, min(3.5, duration / 22.0)) if duration > 0 else 1.5
    vf_base = f"setpts=PTS/{speed:.2f},fps=10,scale=540:-1:flags=lanczos"
    p1 = subprocess.run(
        [ffmpeg, "-y", "-i", str(mp4_path), "-vf", f"{vf_base},palettegen=stats_mode=diff", str(palette_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    gif_out = None
    if p1.returncode == 0 and palette_path.is_file():
        p2 = subprocess.run(
            [
                ffmpeg,
                "-y",
                "-i",
                str(mp4_path),
                "-i",
                str(palette_path),
                "-lavfi",
                f"{vf_base} [x]; [x][1:v] paletteuse=dither=bayer:bayer_scale=3",
                str(gif_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if p2.returncode == 0 and gif_path.is_file():
            gif_out = gif_path
        palette_path.unlink(missing_ok=True)
    return cs_out, gif_out


def render_scene(run_dir: Path, scene_class: str, quality: str = "m") -> dict[str, Any]:
    """Render ``neon_scene.py`` via Manim in a secret-scrubbed subprocess."""
    manim_bin = shutil.which("manim")
    if not manim_bin:
        return {"ok": False, "error": "manim executable not found on PATH"}

    scene_file = run_dir / SCENE_FILE
    if not scene_file.is_file():
        return {"ok": False, "error": f"missing scene file: {scene_file}"}

    media_dir = run_dir / "media"
    cmd = [
        manim_bin,
        f"-q{quality}",
        "--media_dir",
        str(media_dir),
        str(scene_file),
        scene_class,
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(run_dir),
        env=scrubbed_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    (run_dir / "render.log").write_text(
        (proc.stdout or "") + "\n--- STDERR ---\n" + (proc.stderr or ""),
        encoding="utf-8",
    )
    if proc.returncode != 0:
        tail = "\n".join(((proc.stderr or "") + "\n" + (proc.stdout or "")).splitlines()[-25:])
        return {"ok": False, "error": f"manim exited with code {proc.returncode}", "log_tail": tail}

    candidates = sorted(
        (p for p in media_dir.rglob(f"{scene_class}.mp4") if "partial_movie_files" not in p.parts),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        return {"ok": False, "error": f"manim succeeded but {scene_class}.mp4 was not found under {media_dir}"}

    mp4_path = candidates[0]
    final_mp4 = run_dir / f"{scene_class}.mp4"
    if mp4_path.resolve() != final_mp4.resolve():
        shutil.copy2(mp4_path, final_mp4)

    probe = _probe_video(final_mp4)
    duration = float(probe.get("duration_seconds") or 0.0)
    cs_path, gif_path = _generate_contact_sheet_and_gif(final_mp4, run_dir, duration)

    return {
        "ok": True,
        "video_path": str(final_mp4),
        "contact_sheet_path": str(cs_path) if cs_path else None,
        "gif_path": str(gif_path) if gif_path else None,
        **probe,
    }


def publish_film(
    run_dir: Path,
    repo_root: Path,
    slug: str,
    plan: NeonPlan,
    manifest: NeonManifest,
) -> dict[str, str]:
    """Publish MP4, highlights GIF, contact sheet, scene source, and showcase docs."""
    assets_dir = repo_root / "docs" / "assets" / slug
    src_dir = assets_dir / "src"
    showcase_dir = repo_root / "docs" / "showcase" / slug
    src_dir.mkdir(parents=True, exist_ok=True)
    showcase_dir.mkdir(parents=True, exist_ok=True)

    published: dict[str, str] = {}

    if manifest.video_path and Path(manifest.video_path).is_file():
        dst = assets_dir / f"{slug}.mp4"
        shutil.copy2(manifest.video_path, dst)
        published["mp4"] = dst.relative_to(repo_root).as_posix()

    if manifest.gif_path and Path(manifest.gif_path).is_file():
        dst = assets_dir / f"{slug}.gif"
        shutil.copy2(manifest.gif_path, dst)
        published["gif"] = dst.relative_to(repo_root).as_posix()

    if manifest.contact_sheet_path and Path(manifest.contact_sheet_path).is_file():
        dst = assets_dir / "contact-sheet.png"
        shutil.copy2(manifest.contact_sheet_path, dst)
        published["contact_sheet"] = dst.relative_to(repo_root).as_posix()

    scene_src = run_dir / SCENE_FILE
    if scene_src.is_file():
        py_name = slug.replace("-", "_") + ".py"
        dst = src_dir / py_name
        shutil.copy2(scene_src, dst)
        published["scene_source"] = dst.relative_to(repo_root).as_posix()

    for name in (PLAN_FILE, VALIDATION_FILE, TOOL_LOG_FILE, MANIFEST_FILE):
        src_f = run_dir / name
        if src_f.is_file():
            shutil.copy2(src_f, showcase_dir / name)

    readme = showcase_dir / "README.md"
    acts_md = "\n".join(
        f"{a.act}. **{a.title}** (~{a.duration_seconds:.0f}s) — {a.caption}" for a in plan.acts
    )
    readme.write_text(
        f"# {plan.title}\n\n"
        f"*{plan.subtitle}*\n\n"
        f"- **Model:** `{manifest.model}` (`{manifest.backend}` backend)\n"
        f"- **Run ID:** `{manifest.run_id}`\n"
        f"- **Duration:** `{manifest.duration_seconds or 'n/a'}s` ({manifest.resolution or 'n/a'})\n"
        f"- **MP4:** [`{published.get('mp4', '')}`](../../assets/{slug}/{slug}.mp4)\n"
        f"- **Scene source:** [`{published.get('scene_source', '')}`](../../assets/{slug}/src/{slug.replace('-', '_')}.py)\n\n"
        f"## Core Thesis\n\n{plan.core_thesis}\n\n"
        f"## Verification Status\n\n{plan.verification_status}\n\n"
        f"## Acts\n\n{acts_md}\n",
        encoding="utf-8",
    )
    published["showcase_readme"] = readme.relative_to(repo_root).as_posix()
    return published
