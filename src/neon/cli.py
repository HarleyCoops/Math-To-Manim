"""Command line for the Gemini 4 Neon-first Math-To-Manim pipeline.

Examples:
    math-to-manim-neon doctor
    math-to-manim-neon run "Explain the Nov 2026 Riemann Hypothesis proof" --render -q m --publish --slug riemann-hypothesis-2026
    math-to-manim-neon runs
    math-to-manim-neon status <run-id>
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
from pathlib import Path

from neon import __version__
from neon.harness import NeonHarness, default_runs_dir
from neon.models import MANIFEST_FILE, NeonManifest, NeonRequest
from neon.settings import default_backend, default_model, default_thinking_budget, has_gemini_api_cli, resolve_api_key


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="math-to-manim-neon",
        description="Gemini 4 Neon-first single-CLI mathematical film pipeline.",
    )
    parser.add_argument("--version", action="version", version=f"math-to-manim-neon {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Plan, verify, codegen, render, and optionally publish a film in one Neon CLI call")
    run.add_argument("prompt", help="Mathematical topic or film brief")
    run.add_argument("--model", default=default_model(), help="Gemini model ID (default: gemini-4-neon)")
    run.add_argument(
        "--backend",
        default=default_backend(),
        choices=["auto", "genai", "gemini-api", "operator"],
        help="Execution backend (default: auto)",
    )
    run.add_argument("--workspace", help="Operator workspace directory containing 01_neon_plan.json & neon_scene.py")
    run.add_argument("--render", action="store_true", help="Render the validated ThreeDScene with Manim")
    run.add_argument("-q", "--quality", default="m", choices=["l", "m", "h", "p", "k"], help="Manim quality (default: m = 720p30)")
    run.add_argument("--max-repairs", default=3, type=int, choices=range(6))
    run.add_argument("--publish", action="store_true", help="Publish MP4, GIF, contact sheet, and showcase docs")
    run.add_argument("--slug", help="Output slug for run folder and docs/assets/<slug>/")
    run.add_argument("--thinking-budget", type=int, default=default_thinking_budget())

    runs = sub.add_parser("runs", help="List recent Neon runs")
    runs.add_argument("--limit", type=int, default=20)

    status = sub.add_parser("status", help="Inspect one Neon run manifest")
    status.add_argument("run_id")

    sub.add_parser("doctor", help="Check Gemini 4 Neon backends, Manim, LaTeX, and FFmpeg")
    return parser


def _doctor() -> int:
    key, key_source = resolve_api_key()
    checks = {
        "model": default_model(),
        "google_genai_installed": importlib.util.find_spec("google.genai") is not None,
        "gemini_api_cli": has_gemini_api_cli(),
        "api_key_configured": bool(key),
        "api_key_source": key_source if key else None,
        "manim": shutil.which("manim"),
        "ffmpeg": shutil.which("ffmpeg"),
        "ffprobe": shutil.which("ffprobe"),
        "pdflatex": shutil.which("pdflatex"),
    }
    print(json.dumps(checks, indent=2))
    ready = bool(checks["manim"] and checks["ffmpeg"])
    return 0 if ready else 1


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    runs_dir = default_runs_dir()

    if args.command == "doctor":
        return _doctor()

    if args.command == "runs":
        if not runs_dir.is_dir():
            return 0
        manifests = sorted(runs_dir.glob(f"*/{MANIFEST_FILE}"), reverse=True)[: max(1, args.limit)]
        for mf in manifests:
            data = json.loads(mf.read_text(encoding="utf-8"))
            st = data.get("status", {})
            print(f"{data.get('run_id')}\t{st.get('run')}/{st.get('outcome')}\t{data.get('model')}\t{data.get('prompt', '')[:60]}")
        return 0

    if args.command == "status":
        mf = runs_dir / args.run_id / MANIFEST_FILE
        if not mf.is_file():
            raise SystemExit(f"run not found: {args.run_id}")
        print(NeonManifest.model_validate_json(mf.read_text(encoding="utf-8")).model_dump_json(indent=2))
        return 0

    req = NeonRequest(
        prompt=args.prompt,
        model=args.model,
        backend=args.backend,
        render=args.render,
        quality=args.quality,
        max_repairs=args.max_repairs,
        publish=args.publish,
        slug=args.slug,
        workspace=args.workspace,
        thinking_budget=args.thinking_budget,
    )
    result = NeonHarness(runs_dir=runs_dir).run(req)
    print(json.dumps(result, indent=2))
    return 0 if result.get("status", {}).get("run") == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
