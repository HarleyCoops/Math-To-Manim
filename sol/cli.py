"""Command line for the independent GPT-5.6 Sol silo."""

from __future__ import annotations

import argparse

from sol import __version__
from sol.models import CalculationRequest
from sol.service import SolService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="math-to-manim-sol", description="Calculate, verify, and compile with GPT-5.6 Sol.")
    parser.add_argument("--version", action="version", version=f"math-to-manim-sol {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    calculate = sub.add_parser("calculate")
    calculate.add_argument("problem")
    calculate.add_argument("--audience", default="student", choices=["student", "technical", "expert"])
    calculate.add_argument("--reasoning-effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"])
    calculate.add_argument("--offline", action="store_true")
    calculate.add_argument("--render", action="store_true")

    serve = sub.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8656)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "calculate":
        response = SolService().calculate(CalculationRequest(
            problem=args.problem,
            audience=args.audience,
            reasoning_effort=args.reasoning_effort,
            offline=args.offline,
            render=args.render,
        ))
        print(response.model_dump_json(indent=2))
        return 0
    try:
        import uvicorn
    except ImportError:
        raise SystemExit("Install the API extra: pip install -e '.[api]'")
    uvicorn.run("sol.api:app", host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
