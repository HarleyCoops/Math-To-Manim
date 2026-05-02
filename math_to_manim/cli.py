"""Command-line entrypoint for Math-To-Manim."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from math_to_manim.config import RuntimeConfig
from math_to_manim.pipeline.runner import AnimationPipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="math-to-manim")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="Generate a typed animation run")
    generate.add_argument("prompt", help="Short educational animation prompt")
    generate.add_argument("--audience-level", default="high_school")
    generate.add_argument("--duration", type=int, default=60)
    generate.add_argument("--style", default="cinematic")
    generate.add_argument("--quality", default=None, help="Manim quality flag: l, m, h, p, or k")
    generate.add_argument("--model", default=None)
    generate.add_argument("--runs-dir", type=Path, default=None)
    generate.add_argument("--no-render", action="store_true", help="Skip Manim execution")
    generate.add_argument("--deterministic", action="store_true", help="Do not call model adapters")

    inspect_run = subparsers.add_parser("inspect-run", help="Print a run manifest")
    inspect_run.add_argument("run_dir", type=Path)

    return parser


def run_generate(args: argparse.Namespace) -> int:
    config = RuntimeConfig.from_env()
    if args.model:
        config = RuntimeConfig(**{**config.__dict__, "model": args.model})
    if args.runs_dir:
        config = RuntimeConfig(**{**config.__dict__, "runs_dir": args.runs_dir})
    if args.quality:
        config = RuntimeConfig(**{**config.__dict__, "default_quality": args.quality})
    if args.deterministic:
        config = RuntimeConfig(**{**config.__dict__, "deterministic": True})

    pipeline = AnimationPipeline(config=config)
    package = pipeline.generate(
        prompt=args.prompt,
        audience_level=args.audience_level,
        desired_duration=args.duration,
        style=args.style,
        render=not args.no_render,
    )
    print(json.dumps(package.to_public_dict(), indent=2))
    return 0


def run_inspect(args: argparse.Namespace) -> int:
    manifest = args.run_dir / "manifest.json"
    if not manifest.exists():
        raise SystemExit(f"No manifest found at {manifest}")
    print(manifest.read_text(encoding="utf-8"))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "generate":
        return run_generate(args)
    if args.command == "inspect-run":
        return run_inspect(args)
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
