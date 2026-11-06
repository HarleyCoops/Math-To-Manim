"""Command line for the independent Grok-native Math To Manim silo."""

from __future__ import annotations

import argparse
import json

from grok import __version__
from grok.client import XAIClient, api_key_status
from grok.models import MAX_REPAIRS, QUALITIES, REASONING_EFFORTS, RunRequest
from grok.service import GrokService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="math-to-manim-grok",
        description="Produce Manim explainers through the Grok 4.6 xAI Responses API.",
    )
    parser.add_argument("--version", action="version", version=f"math-to-manim-grok {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Create one complete Grok film-production run")
    run.add_argument("prompt")
    run.add_argument("--image", help="Photographed homework page or diagram")
    run.add_argument("--render", action="store_true")
    run.add_argument("-q", "--quality", default="l", choices=list(QUALITIES))
    run.add_argument(
        "--reasoning-effort",
        default=None,
        choices=list(REASONING_EFFORTS),
        help="Grok reasoning effort (default: XAI_REASONING_EFFORT, else high)",
    )
    run.add_argument("--max-repairs", default=2, type=int, choices=range(0, MAX_REPAIRS + 1))
    run.add_argument("--offline", action="store_true")

    runs = sub.add_parser("runs", help="List recent Grok run manifests")
    runs.add_argument("--limit", type=int, default=20)

    status = sub.add_parser("status", help="Show one Grok run manifest")
    status.add_argument("run_id")

    sub.add_parser("doctor", help="Live-ping xAI when XAI_API_KEY is set, without printing it")
    return parser


def _doctor() -> int:
    """Check the key is set, then live-ping xAI. The key itself is never printed."""
    ok, detail = api_key_status()
    if not ok:
        print(f"not ready: {detail}")
        return 1
    client = XAIClient()
    ok, detail = client.ping()
    if not ok:
        print(f"not ready: {detail}")
        print(f"endpoint: {client.base_url}/responses")
        return 1
    print(f"ready: {detail}; model={client.model}; reasoning_effort={client.reasoning_effort}")
    print(f"endpoint: {client.base_url}/responses")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    service = GrokService()
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
