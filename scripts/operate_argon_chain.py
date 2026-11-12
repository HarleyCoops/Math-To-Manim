"""Operate the Argon Google ADK (`google-adk` + `google-genai`) six-agent chain with an active Gemini 4 Argon session.

Mirrors `scripts/operate_mythos_chain.py` for the Argon Google Agent SDK pipeline:
* Writes each stage's prompt (`NN_*.prompt.txt`) from the Argon stage table and charters;
* Validates every stage artifact (`01_intent.json` .. `06_scene_spec.json`, including reverse-tree validation on `02_knowledge_map.json`);
* Replays the ADK function tools (`execute_math_check` on all math-director expressions and `verify_scene` on `argon_scene.py`);
* Records the complete validated run bundle under `runs/argon/<timestamp>-<slug>/` and optionally renders the MP4 via Manim.

Requires the package to be installed (`pip install -e .`); google-adk is not needed.

Usage:
    python scripts/operate_argon_chain.py path/to/stages
    python scripts/operate_argon_chain.py path/to/stages --render -q h
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Callable
from pathlib import Path

from argon import bundle
from argon.models import SCENE_FILE, SDK_NAME
from argon.stages import COMPOSER, STAGES, Stage, stage_prompt
from argon.tools import execute_math_check, verify_scene

NEEDS_REPLY = 2
NEXT_PROMPT_FILE = "NEXT_PROMPT.txt"


def _log(message: str) -> None:
    print(message, file=sys.stderr)


def _charter_and_prompt(charter: str, prompt: str) -> str:
    return "SYSTEM CHARTER:\n" + charter + "\n\nPROMPT:\n" + prompt


def _ask(stages: Path, filename: str, charter: str, prompt: str) -> int:
    (stages / NEXT_PROMPT_FILE).write_text(_charter_and_prompt(charter, prompt), encoding="utf-8")
    _log(f"  [argon-operator] reply needed: save it as {stages / filename}")
    _log(f"  [argon-operator] prompt written to {stages / NEXT_PROMPT_FILE}")
    return NEEDS_REPLY


# --- tool replay --------------------------------------------------------------
# The operator session cannot call ADK function tools itself, so the script
# replays each stage's tools over the recorded reply and records the calls.


def _replay_math_checks(reply: dict, scene_source: str) -> list[dict]:
    calls: list[dict] = []
    for item in [*reply.get("checks", []), *reply.get("numbers", [])]:
        if isinstance(item, dict) and "expression" in item:
            expression = str(item["expression"])
            calls.append(
                {"tool": "execute_math_check", "input": expression, "output": execute_math_check(expression)}
            )
    return calls


def _replay_verify_scene(reply: dict, scene_source: str) -> list[dict]:
    return [{"tool": "verify_scene", "output": verify_scene(source=scene_source)}]


TOOL_REPLAY: dict[Callable, Callable[[dict, str], list[dict]]] = {
    execute_math_check: _replay_math_checks,
    verify_scene: _replay_verify_scene,
}


def _replay_tools(stage: Stage, reply: dict, scene_source: str) -> list[dict]:
    calls: list[dict] = []
    for tool in stage.tools:
        calls.extend(TOOL_REPLAY[tool](reply, scene_source))
    return calls


# --- operate ------------------------------------------------------------------


def operate(
    stages: Path,
    *,
    runs_dir: Path | None = None,
    model: str = "gemini-4-argon",
    render: bool = False,
    quality: str = "l",
) -> tuple[int, Path | None]:
    stages = Path(stages).resolve()
    prompt_file = stages / "prompt.txt"
    if not prompt_file.is_file():
        raise SystemExit(f"missing production prompt: {prompt_file}")
    prompt = prompt_file.read_text(encoding="utf-8").replace(chr(0xFEFF), "").strip()

    prior: dict[str, dict] = {}
    plan: list[tuple[Stage, str, str, dict]] = []
    for stage in STAGES:
        charter = stage.charter()
        user_text = stage_prompt(stage, prompt, prior)
        reply_path = stages / stage.artifact
        if not reply_path.is_file():
            return _ask(stages, stage.artifact, charter, user_text), None
        reply = json.loads(reply_path.read_text(encoding="utf-8"))
        if not isinstance(reply, dict) or not reply:
            raise SystemExit(f"stage {stage.name!r} rejected: artifact is not a non-empty JSON object")
        try:
            reply = stage.prepare(reply)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        plan.append((stage, charter, user_text, reply))
        prior[stage.artifact] = reply

    scene_path = stages / SCENE_FILE
    if not scene_path.is_file():
        return _ask(stages, SCENE_FILE, COMPOSER.charter(), stage_prompt(COMPOSER, prompt, prior)), None
    scene_source = scene_path.read_text(encoding="utf-8")

    (stages / NEXT_PROMPT_FILE).unlink(missing_ok=True)

    run_dir = bundle.create_run_dir(runs_dir or bundle.default_runs_dir(), prompt)
    manifest = bundle.new_manifest(
        run_dir,
        prompt=prompt,
        model=model,
        backend="argon-operator",
        offline=False,
        render_requested=render,
        quality=quality,
        operator_note=(
            "Stages executed with Gemini 4 Argon acting as the Google ADK model backend "
            "(scripts/operate_argon_chain.py); every stage artifact and ADK tool call was verified by the harness."
        ),
    )
    bundle.write_request(
        run_dir,
        {
            "prompt": prompt,
            "render": render,
            "quality": quality,
            "reasoning_effort": "high",
            "sdk": SDK_NAME,
            "adk_sub_agents": [stage.agent_name for stage in STAGES],
        },
    )

    for stage, charter, user_text, reply in plan:
        stem = stage.artifact.split(".")[0]
        (run_dir / f"{stem}.prompt.txt").write_text(_charter_and_prompt(charter, user_text), encoding="utf-8")
        bundle.write_artifact(run_dir, stage, reply)
        tool_calls = _replay_tools(stage, reply, scene_source)
        bundle.write_trace(
            run_dir,
            stage.name,
            {
                "stage": stage.name,
                "sdk": "google-adk",
                "adk_agent_name": stage.agent_name,
                "adk_output_key": stage.artifact,
                "model": model,
                "tool_calls": tool_calls,
            },
        )
        manifest.stages.append(
            {
                "stage": stage.name,
                "artifact": stage.artifact,
                "adk_agent": stage.agent_name,
                "bytes": len(json.dumps(reply)),
                "tool_calls": len(tool_calls),
            }
        )
        _log(f"  [argon-adk] {stage.name:<16} -> {stage.artifact} (valid, agent={stage.agent_name})")

    bundle.write_scene(run_dir, scene_source)

    failures, scene_name = bundle.validate_run(run_dir)
    _log(
        f"  [argon-adk] composer         -> {SCENE_FILE} ({scene_name}); static check "
        f"{'passed' if not failures else 'FAILED: ' + '; '.join(failures)}"
    )
    if failures:
        bundle.fail_manifest(run_dir, manifest, "; ".join(failures))
        return 1, run_dir
    assert scene_name is not None

    video_path = None
    review_extra: dict = {}
    if render:
        from argon.render import render_scene

        started = time.time()
        try:
            video_path = render_scene(run_dir, scene_name, quality)
        except Exception as exc:
            bundle.fail_manifest(run_dir, manifest, str(exc))
            raise
        review_extra["render_seconds"] = round(time.time() - started, 1)
        _log(f"  [argon-adk] rendered ({quality}) -> {video_path} in {review_extra['render_seconds']}s")

    bundle.write_validation(run_dir)
    bundle.write_review(
        run_dir,
        offline=False,
        model=model,
        video_path=video_path,
        checks=bundle.VALIDATION_CHECKS + ("execute_math_check",),
        **review_extra,
    )
    bundle.complete_manifest(run_dir, manifest, scene_name=scene_name, video_path=video_path)
    _log(f"  [argon-adk] run recorded -> {run_dir}")
    return 0, run_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("stages", type=Path, help="directory holding prompt.txt and the stage replies")
    parser.add_argument("--runs-dir", type=Path, default=None)
    parser.add_argument("--model", default="gemini-4-argon", help="model recorded in the manifest")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("-q", "--quality", default="l", choices=list("lmhpk"))
    args = parser.parse_args(argv)
    rc, _ = operate(
        args.stages,
        runs_dir=args.runs_dir,
        model=args.model,
        render=args.render,
        quality=args.quality,
    )
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
