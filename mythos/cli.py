"""The math-to-manim command line.

    math-to-manim run "explain quantum field theory" --render -q m
    math-to-manim run "the heat equation" --offline
    math-to-manim runs                      # list on-disk runs
    math-to-manim serve-api                 # REST API on :8642
    math-to-manim serve-mcp                 # MCP server on stdio
"""

from __future__ import annotations

import argparse
import json
import sys

from mythos import __version__
from mythos.backends import DEFAULT_COMMAND, DEFAULT_MODEL, DEFAULT_TIMEOUT


def _cmd_run(args: argparse.Namespace) -> int:
    from mythos.harness import MythosHarness

    harness = MythosHarness(command=args.command, model=args.model,
                            timeout=args.timeout, offline=args.offline)
    harness.run(args.prompt, render=args.render, quality=args.quality,
                max_repairs=args.max_repairs)
    return 0


def _cmd_runs(args: argparse.Namespace) -> int:
    from mythos.service import MythosService

    summaries = MythosService().list_runs(limit=args.limit)
    print(json.dumps(summaries, indent=2))
    return 0


def _cmd_serve_api(args: argparse.Namespace) -> int:
    try:
        import uvicorn
    except ImportError:
        print("The REST API requires the 'api' extra: pip install -e '.[api]'",
              file=sys.stderr)
        return 1
    uvicorn.run("mythos.api:app", host=args.host, port=args.port,
                reload=args.reload)
    return 0


def _cmd_serve_mcp(args: argparse.Namespace) -> int:
    from mythos.mcp_server import main as mcp_main

    mcp_main(transport=args.transport, port=args.port)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="math-to-manim",
        description="Ask a question -> get a freakin' movie.",
    )
    parser.add_argument("--version", action="version",
                        version=f"math-to-manim {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="Run the Mythos 6-agent chain on a prompt")
    run.add_argument("prompt")
    run.add_argument("--render", action="store_true")
    run.add_argument("-q", "--quality", default="l", choices=list("lmhpk"))
    run.add_argument("--model", default=DEFAULT_MODEL)
    run.add_argument("--command", default=DEFAULT_COMMAND)
    run.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    run.add_argument("--offline", action="store_true")
    run.add_argument("--max-repairs", type=int, default=3)
    run.set_defaults(func=_cmd_run)

    runs = sub.add_parser("runs", help="List on-disk runs, newest first")
    runs.add_argument("--limit", type=int, default=20)
    runs.set_defaults(func=_cmd_runs)

    api = sub.add_parser("serve-api", help="Serve the REST API (FastAPI)")
    api.add_argument("--host", default="127.0.0.1")
    api.add_argument("--port", type=int, default=8642)
    api.add_argument("--reload", action="store_true")
    api.set_defaults(func=_cmd_serve_api)

    mcp = sub.add_parser("serve-mcp", help="Serve the MCP server")
    mcp.add_argument("--transport", default="stdio",
                     choices=["stdio", "streamable-http"])
    mcp.add_argument("--port", type=int, default=8643)
    mcp.set_defaults(func=_cmd_serve_mcp)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
