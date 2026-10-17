"""Command line for the Argon Google Agent SDK (`google-adk` + `google-genai`) silo."""

from __future__ import annotations

import argparse
import json
import os

from argon import __version__
from argon.client import DEFAULT_MODEL, DEFAULT_REASONING_EFFORT, ArgonClient, api_key_status, resolve_api_key
from argon.models import REASONING_EFFORTS, RunRequest
from argon.service import ArgonService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="math-to-manim-argon",
        description="Produce Manim films through the Argon Google Agent SDK (google-adk + google-genai).",
    )
    parser.add_argument("--version", action="version", version=f"math-to-manim-argon {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Create one complete Argon Google ADK film-production run")
    run.add_argument("prompt")
    run.add_argument("--image", help="Optional image or diagram attachment")
    run.add_argument("--render", action="store_true")
    run.add_argument("-q", "--quality", default="l", choices=["l", "m", "h", "p", "k"])
    run.add_argument(
        "--reasoning-effort",
        default=DEFAULT_REASONING_EFFORT,
        choices=list(REASONING_EFFORTS),
    )
    run.add_argument("--max-repairs", default=2, type=int, choices=range(0, 6))
    run.add_argument("--offline", action="store_true")

    runs = sub.add_parser("runs", help="List recent Argon run manifests")
    runs.add_argument("--limit", type=int, default=20)

    status = sub.add_parser("status", help="Show one Argon run manifest")
    status.add_argument("run_id")

    sub.add_parser("doctor", help="Check google-adk + google-genai and live-ping when GEMINI_API_KEY is set")
    return parser


def _doctor() -> int:
    ok, detail = api_key_status()
    model = os.getenv("ARGON_MODEL", DEFAULT_MODEL)
    effort = os.getenv("ARGON_REASONING_EFFORT", DEFAULT_REASONING_EFFORT)
    key, _ = resolve_api_key()
    if not ok:
        print(f"not ready: {detail}")
        return 1
    client = ArgonClient()
    ok, detail = client.ping()
    if key and key in detail:
        print("not ready: doctor refused to describe the key")
        return 1
    if not ok:
        print(f"not ready: {detail}")
        return 1
    print(f"ready: {detail}; sdk=google-adk+google-genai; model={model}; reasoning_effort={effort}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    service = ArgonService()
    if args.command == "run":
        response = service.run(
            RunRequest(
                prompt=args.prompt,
                image=args.image,
                reasoning_effort=args.reasoning_effort,
                offline=args.offline,
                render=args.render,
                quality=args.quality,
                max_repairs=args.max_repairs,
            )
        )
        print(json.dumps(response, indent=2))
        return 0
    if args.command == "runs":
        for manifest in service.list_runs(limit=max(1, args.limit)):
            print(f"{manifest.run_id}\t{manifest.status}\t{manifest.prompt}")
        return 0
    if args.command == "status":
        print(service.get_run(args.run_id).model_dump_json(indent=2))
        return 0
    return _doctor()


if __name__ == "__main__":
    raise SystemExit(main())
