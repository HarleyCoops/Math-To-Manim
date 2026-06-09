"""Convert a Math-To-Manim run into Atlas Cloud text-to-video prompts.

The pipeline produces structured JSON per run (``storyboard.json`` for visual
intent, ``scene_spec.json`` for the animation timeline). Atlas Cloud's
``google/gemini-omni-flash/text-to-video-developer`` model is an omni model: it
renders motion *and* native audio from a single prompt written in a
``System / Style`` + ``Visual & Action Sequence`` + ``Audio & Sound Sync``
grammar with timestamped beats.

This module is the converter from run artifacts to that grammar. It deliberately
keeps math formulas *out* of the video prompt (diffusion models render LaTeX as
noise) and emits a parallel ``overlay`` track so the exact equations can be
composited back on top, timed from the animation spec.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import time
from typing import Any, Optional

import requests

ATLAS_BASE_URL = os.getenv("ATLASCLOUD_BASE_URL", "https://api.atlascloud.ai")
ATLAS_MODEL = os.getenv(
    "ATLASCLOUD_VIDEO_MODEL", "google/gemini-omni-flash/text-to-video-developer"
)
ALLOWED_DURATIONS = (4, 6, 8, 10)

# Manim animation verbs -> natural-language motion the video model understands.
_ACTION_VERBS = {
    "FadeIn": "fades into view",
    "FadeOut": "fades away",
    "Create": "is drawn in",
    "Uncreate": "is erased",
    "Write": "appears as if written",
    "DrawBorderThenFill": "is outlined then filled",
    "Indicate": "pulses to draw the eye",
    "Flash": "flashes briefly",
    "Circumscribe": "is briefly framed",
    "Transform": "smoothly transforms",
    "ReplacementTransform": "morphs into the next form",
    "TransformMatchingTex": "rearranges term by term",
    "GrowFromCenter": "grows from its center",
    "GrowArrow": "extends outward",
    "LaggedStart": "appear in staggered succession",
    "MoveAlongPath": "glides along a path",
    "Rotate": "rotates in place",
    "ApplyWave": "ripples with a wave",
}


def _humanize(token: str) -> str:
    return token.replace("_", " ").strip() if token else ""


def snap_duration(seconds: Optional[float]) -> int:
    """Snap an arbitrary scene length to the nearest model-allowed duration."""

    if not seconds or seconds <= 0:
        return 8
    # Nearest allowed value; ties round up so we never clip content.
    return min(ALLOWED_DURATIONS, key=lambda d: (abs(d - seconds), -d))


def _fmt_ts(seconds: float) -> str:
    seconds = max(0.0, seconds)
    return f"{int(seconds // 60)}:{int(round(seconds % 60)):02d}"


@dataclass
class OverlayCue:
    """A formula/text overlay to composite on top of the rendered clip."""

    latex: str
    start: float
    end: float
    position: str = "top-right"

    def to_dict(self) -> dict[str, Any]:
        return {
            "latex": self.latex,
            "start": round(self.start, 2),
            "end": round(self.end, 2),
            "position": self.position,
        }


@dataclass
class ClipPlan:
    """One Atlas Cloud video request plus its companion overlay track."""

    scene_id: str
    title: str
    payload: dict[str, Any]
    overlays: list[OverlayCue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "scene_id": self.scene_id,
            "title": self.title,
            "payload": self.payload,
            "overlays": [o.to_dict() for o in self.overlays],
        }


def _bucket_animations(scene_spec: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    buckets: dict[str, list[dict[str, Any]]] = {}
    for anim in scene_spec.get("animations", []):
        scene_id = (anim.get("metadata") or {}).get("scene")
        if scene_id:
            buckets.setdefault(scene_id, []).append(anim)
    return buckets


def _scene_span(scene: dict[str, Any], anims: list[dict[str, Any]]) -> float:
    span = scene.get("duration_seconds")
    if span:
        return float(span)
    end = 0.0
    for a in anims:
        start = float(a.get("start_time") or 0.0)
        end = max(end, start + float(a.get("duration_seconds") or 0.0))
    return end or 8.0


def _style_block(storyboard_meta: dict[str, Any]) -> str:
    style = storyboard_meta.get("visual_style", "clean mathematical motion graphics")
    audience = storyboard_meta.get("audience")
    palette = storyboard_meta.get("color_palette") or {}
    palette_str = ", ".join(f"{_humanize(k)} {v}" for k, v in palette.items())
    parts = [
        f"Abstract mathematical motion graphics. {style}.",
        f"Color palette: {palette_str}." if palette_str else "",
        f"Pitched for a {audience} audience." if audience else "",
        "Smooth deliberate camera, high contrast, clean negative space.",
        "Do NOT render any text, letters, digits, axis numbers, labels, captions, "
        "watermarks, resolution tags, or equations anywhere in frame — all text is added in post.",
    ]
    return "System / Style: " + " ".join(p for p in parts if p)


def _action_block(
    scene: dict[str, Any], anims: list[dict[str, Any]], span: float, clip_dur: int
) -> str:
    meta = scene.get("metadata") or {}
    scale = (clip_dur / span) if span else 1.0
    lead = meta.get("visual_metaphor") or scene.get("title") or ""
    objects = [
        o for o in (meta.get("objects") or scene.get("visual_actions") or [])
        if not _is_formula(str(o))
    ]
    camera = scene.get("camera") or ""
    transition = meta.get("transition") or ""

    beats: list[str] = []
    for anim in sorted(anims, key=lambda a: float(a.get("start_time") or 0.0)):
        target = anim.get("target") or ""
        if _is_formula(target):  # formulas live on the overlay track, not here
            continue
        verb = _ACTION_VERBS.get(anim.get("action", ""), "animates")
        start = float(anim.get("start_time") or 0.0) * scale
        end = (start + float(anim.get("duration_seconds") or 0.0) * scale)
        subject = _humanize(target) or "the focal element"
        cam = (anim.get("metadata") or {}).get("camera")
        beat = f"{_fmt_ts(start)}-{_fmt_ts(end)}: {subject} {verb}"
        if cam:
            beat += f"; camera {cam}"
        beats.append(beat)

    lines = [f"Visual & Action Sequence: {lead}"]
    if objects:
        lines.append("Elements in frame: " + ", ".join(map(str, objects)) + ".")
    if camera:
        lines.append(f"Camera: {camera}")
    if beats:
        lines.append("Timed beats:")
        lines.extend(f"  {b}" for b in beats)
    if transition:
        lines.append(f"Transition out: {transition}")
    return "\n".join(lines)


def _audio_block(scene: dict[str, Any], clip_dur: int) -> str:
    narration = (scene.get("narration") or "").strip()
    lines = ["Audio & Sound Sync:"]
    if narration:
        lines.append(
            f"0:00-{_fmt_ts(clip_dur)}: Calm, clear narrator voiceover: \"{narration}\""
        )
    lines.append(
        "Underscore with subtle, airy ambient pads and soft UI ticks synced to each "
        "element entrance; no music stings that fight the narration."
    )
    return "\n".join(lines)


def _is_formula(target: str) -> bool:
    t = (target or "").lower()
    return any(
        k in t
        for k in ("formula", "equation", "eq_", "mathtex", "tex", "label", "title", "text", "overlay")
    )


def _overlay_cues(
    scene: dict[str, Any], anims: list[dict[str, Any]], span: float, clip_dur: int
) -> list[OverlayCue]:
    meta = scene.get("metadata") or {}
    equations = list(meta.get("equation_overlays") or [])
    if not equations:
        return []
    scale = (clip_dur / span) if span else 1.0
    position = _overlay_position(scene)

    # Prefer real timings from formula-targeted animations; fall back to an even
    # spread across the clip so every equation still gets screen time.
    formula_anims = sorted(
        (a for a in anims if _is_formula(a.get("target") or "")),
        key=lambda a: float(a.get("start_time") or 0.0),
    )
    cues: list[OverlayCue] = []
    if len(formula_anims) >= len(equations):
        for latex, anim in zip(equations, formula_anims):
            start = float(anim.get("start_time") or 0.0) * scale
            cues.append(OverlayCue(latex=latex, start=start, end=clip_dur, position=position))
    else:
        step = clip_dur / max(1, len(equations))
        for i, latex in enumerate(equations):
            cues.append(
                OverlayCue(latex=latex, start=i * step, end=clip_dur, position=position)
            )
    return cues


def _overlay_position(scene: dict[str, Any]) -> str:
    # Honour an explicit hint, else default to the storyboard convention
    # ("fixed-in-frame formulas, top right").
    hint = json.dumps(scene.get("metadata") or {}).lower()
    if "bottom" in hint:
        return "bottom-center"
    return "top-right"


def build_clip_plans(
    run_dir: str | Path,
    *,
    aspect_ratio: str = "16:9",
    resolution: str = "720p",
    seed: int = -1,
) -> list[ClipPlan]:
    """Convert a run directory's artifacts into one ClipPlan per storyboard scene."""

    run_dir = Path(run_dir)
    storyboard = json.loads((run_dir / "storyboard.json").read_text(encoding="utf-8"))
    spec_path = run_dir / "scene_spec.json"
    scene_spec = (
        json.loads(spec_path.read_text(encoding="utf-8")) if spec_path.exists() else {}
    )
    sb_meta = storyboard.get("metadata") or {}
    buckets = _bucket_animations(scene_spec)

    plans: list[ClipPlan] = []
    for scene in storyboard.get("scenes", []):
        scene_id = scene.get("id") or scene.get("title") or f"scene_{len(plans) + 1}"
        anims = buckets.get(scene_id, [])
        span = _scene_span(scene, anims)
        clip_dur = snap_duration(span)

        prompt = "\n\n".join(
            [
                _style_block(sb_meta),
                _action_block(scene, anims, span, clip_dur),
                _audio_block(scene, clip_dur),
            ]
        )[:20000]

        payload = {
            "model": ATLAS_MODEL,
            "prompt": prompt,
            "duration": clip_dur,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "seed": seed,
        }
        plans.append(
            ClipPlan(
                scene_id=scene_id,
                title=scene.get("title", scene_id),
                payload=payload,
                overlays=_overlay_cues(scene, anims, span, clip_dur),
            )
        )
    return plans


def write_plans(run_dir: str | Path, plans: list[ClipPlan]) -> Path:
    out = Path(run_dir) / "atlas_video_prompts.json"
    out.write_text(
        json.dumps(
            {
                "model": ATLAS_MODEL,
                "scene_count": len(plans),
                "clips": [p.to_dict() for p in plans],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return out


class AtlasVideoClient:
    """Thin client for the Atlas Cloud generateVideo + prediction-poll endpoints."""

    def __init__(self, api_key: Optional[str] = None, base_url: str = ATLAS_BASE_URL):
        self.api_key = api_key or os.getenv("ATLASCLOUD_API_KEY")
        if not self.api_key:
            raise RuntimeError("Set ATLASCLOUD_API_KEY (env) or pass api_key=...")
        self.base_url = base_url.rstrip("/")

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def submit(self, payload: dict[str, Any]) -> str:
        resp = requests.post(
            f"{self.base_url}/api/v1/model/generateVideo",
            headers=self._headers,
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["data"]["id"]

    def poll(self, request_id: str, *, interval: float = 2.0, timeout: float = 900.0) -> str:
        deadline = time.monotonic() + timeout
        url = f"{self.base_url}/api/v1/model/prediction/{request_id}"
        while True:
            data = requests.get(url, headers=self._headers, timeout=60).json()["data"]
            status = data.get("status")
            if status in ("completed", "succeeded"):
                return data["outputs"][0]
            if status in ("failed", "timeout"):
                raise RuntimeError(data.get("error") or f"generation {status}")
            if time.monotonic() > deadline:
                raise TimeoutError(f"prediction {request_id} timed out")
            time.sleep(interval)

    def generate(self, payload: dict[str, Any]) -> str:
        return self.poll(self.submit(payload))

    def download(self, url: str, dest: str | Path) -> Path:
        dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with requests.get(url, stream=True, timeout=300) as r:
            r.raise_for_status()
            with dest.open("wb") as fh:
                for chunk in r.iter_content(chunk_size=1 << 20):
                    fh.write(chunk)
        return dest


def render_clips(run_dir: str | Path, plans: list[ClipPlan]) -> list[dict[str, Any]]:
    """Submit every clip to Atlas Cloud and download the resulting mp4s."""

    client = AtlasVideoClient()
    clips_dir = Path(run_dir) / "atlas_clips"
    results: list[dict[str, Any]] = []
    for i, plan in enumerate(plans, start=1):
        url = client.generate(plan.payload)
        local = client.download(url, clips_dir / f"{i:02d}_{plan.scene_id}.mp4")
        results.append({"scene_id": plan.scene_id, "url": url, "path": str(local)})
    (Path(run_dir) / "atlas_render_result.json").write_text(
        json.dumps({"clips": results}, indent=2), encoding="utf-8"
    )
    return results


# x expression + vertical anchor per named position. `slot` stacks concurrent
# overlays into separate rows so they never collide.
_SLOT_H = 110
_OVERLAY_POS = {
    "top-right": ("main_w-overlay_w-40", lambda s: f"40+{s * _SLOT_H}"),
    "top-left": ("40", lambda s: f"40+{s * _SLOT_H}"),
    "bottom-center": ("(main_w-overlay_w)/2", lambda s: f"main_h-overlay_h-40-{s * _SLOT_H}"),
    "bottom-right": ("main_w-overlay_w-40", lambda s: f"main_h-overlay_h-40-{s * _SLOT_H}"),
}


def _overlay_xy(position: str, slot: int) -> str:
    x_expr, y_fn = _OVERLAY_POS.get(position, _OVERLAY_POS["top-right"])
    return f"{x_expr}:{y_fn(slot)}"


def render_formula_png(latex: str, dest: str | Path) -> Path:
    """Render a LaTeX formula to a tight transparent PNG.

    Uses real LaTeX via Manim (crisp Computer Modern, white glyphs with a dark
    background stroke), auto-cropped to the formula and given a soft drop shadow
    for legibility over any background. Falls back to matplotlib mathtext if the
    Manim/LaTeX toolchain is unavailable.
    """

    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        return _render_formula_manim(latex, dest)
    except Exception:
        return _render_formula_matplotlib(latex, dest)


def _render_formula_manim(latex: str, dest: Path) -> Path:
    import subprocess

    from PIL import Image, ImageFilter

    scene_module = Path(__file__).with_name("_formula_scene.py")
    media = dest.parent / ".manim_formula"
    env = {**os.environ, "M2M_FORMULA_TEX": latex}
    subprocess.run(
        ["manim", "-s", "-t", "-qh", "-r", "1920,1080", "--format=png",
         "--media_dir", str(media), str(scene_module), "FormulaScene"],
        check=True, capture_output=True, text=True, env=env,
    )
    pngs = sorted(media.rglob("*.png"), key=lambda p: p.stat().st_mtime)
    if not pngs:
        raise RuntimeError("manim produced no PNG")
    img = Image.open(pngs[-1]).convert("RGBA")
    bbox = img.getbbox()
    if bbox:
        pad = 24
        l, t, r, b = bbox
        img = img.crop((max(0, l - pad), max(0, t - pad),
                        min(img.width, r + pad), min(img.height, b + pad)))
    # Soft drop shadow from the alpha channel so white glyphs read on any background.
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow.putalpha(img.split()[-1].filter(ImageFilter.GaussianBlur(6)))
    out = Image.alpha_composite(shadow, img)
    out.save(dest)
    return dest


def _render_formula_matplotlib(latex: str, dest: Path) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, f"${latex}$", fontsize=22, color="white")
    fig.savefig(dest, dpi=220, transparent=True, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    return dest


def _probe_duration(path: str | Path) -> float:
    import subprocess

    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip() or 0.0)


def composite_clip(
    clip_path: str | Path, overlays: list[OverlayCue], out_path: str | Path
) -> Path:
    """Burn timed formula overlays onto a single rendered clip with ffmpeg."""

    import subprocess

    clip_path, out_path = Path(clip_path), Path(out_path)
    if not overlays:
        out_path.write_bytes(clip_path.read_bytes())
        return out_path

    duration = _probe_duration(clip_path)
    work = out_path.parent / f".{out_path.stem}_overlays"
    work.mkdir(parents=True, exist_ok=True)

    inputs = ["-i", str(clip_path)]
    filters = []
    last = "0:v"
    for i, cue in enumerate(overlays, start=1):
        png = render_formula_png(cue.latex, work / f"f{i}.png")
        inputs += ["-loop", "1", "-i", str(png)]
        xy = _overlay_xy(cue.position, i - 1)
        end = cue.end if cue.end and cue.end > 0 else duration
        out_label = f"v{i}"
        filters.append(
            f"[{last}][{i}:v]overlay={xy}:enable='between(t,{cue.start},{end})'[{out_label}]"
        )
        last = out_label

    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", ";".join(filters),
        "-map", f"[{last}]", "-map", "0:a?",
        "-t", f"{duration}", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", str(out_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return out_path


def concat_clips(clip_paths: list[str | Path], out_path: str | Path) -> Path:
    """Concatenate composited clips into a single final video."""

    import subprocess

    out_path = Path(out_path)
    listfile = out_path.parent / "concat_list.txt"
    listfile.write_text(
        "".join(f"file '{Path(p).resolve()}'\n" for p in clip_paths), encoding="utf-8"
    )
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(out_path)],
        check=True, capture_output=True, text=True,
    )
    return out_path


def composite_run(
    run_dir: str | Path, plans: list[ClipPlan], rendered: list[dict[str, Any]]
) -> Path:
    """Composite every rendered clip's overlays, then concat into final.mp4."""

    run_dir = Path(run_dir)
    out_dir = run_dir / "atlas_final"
    out_dir.mkdir(parents=True, exist_ok=True)
    by_scene = {p.scene_id: p for p in plans}
    composited: list[Path] = []
    for i, clip in enumerate(rendered, start=1):
        plan = by_scene.get(clip["scene_id"])
        overlays = plan.overlays if plan else []
        composited.append(
            composite_clip(clip["path"], overlays, out_dir / f"{i:02d}_{clip['scene_id']}.mp4")
        )
    return concat_clips(composited, run_dir / "final.mp4")


def _cli(argv: list[str]) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run-artifacts -> Atlas Cloud video prompts")
    parser.add_argument("run_dir", help="Path to a runs/<timestamp-...> directory")
    parser.add_argument("--aspect-ratio", default="16:9", choices=["16:9", "9:16"])
    parser.add_argument("--resolution", default="720p", choices=["720p", "1080p", "4k"])
    parser.add_argument("--seed", type=int, default=-1)
    parser.add_argument("--render", action="store_true", help="Submit clips to Atlas Cloud")
    parser.add_argument(
        "--composite", action="store_true",
        help="Burn formula overlays onto rendered clips and concat into final.mp4 (implies --render)",
    )
    args = parser.parse_args(argv)

    plans = build_clip_plans(
        args.run_dir,
        aspect_ratio=args.aspect_ratio,
        resolution=args.resolution,
        seed=args.seed,
    )
    out = write_plans(args.run_dir, plans)
    print(f"Wrote {len(plans)} clip prompts -> {out}")
    for p in plans:
        print(f"  {p.scene_id}: {p.payload['duration']}s, {len(p.overlays)} overlay(s)")
    if args.render or args.composite:
        results = render_clips(args.run_dir, plans)
        print(f"Rendered {len(results)} clips into {Path(args.run_dir) / 'atlas_clips'}")
        if args.composite:
            final = composite_run(args.run_dir, plans, results)
            print(f"Composited final video -> {final}")
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(_cli(sys.argv[1:]))
