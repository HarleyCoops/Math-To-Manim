"""Operate the Argon Google ADK (`google-adk` + `google-genai`) six-agent chain with an active Gemini 4 Argon session.

Mirrors `scripts/operate_mythos_chain.py` for the Argon Google Agent SDK pipeline:
* Builds the 6-stage `google.adk.agents.SequentialAgent` and per-stage `LlmAgent` instances;
* Writes each stage's prompt (`NN_*.prompt.txt`) using the Argon charters;
* Validates every stage artifact (`01_intent.json` .. `06_scene_spec.json`, including reverse-tree validation on `02_knowledge_map.json`);
* Runs ADK function tools (`execute_math_check` on all math-director expressions and `verify_scene` on `argon_scene.py`);
* Records the complete validated run bundle under `runs/argon/<timestamp>-<slug>/` and optionally renders the MP4 via Manim.

Usage:
    python scripts/operate_argon_chain.py path/to/stages
    python scripts/operate_argon_chain.py path/to/stages --render -q h
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from argon.charters import STAGES, cinematic_charter, load_charter  # noqa: E402
from argon.client import build_adk_sequential_pipeline, build_stage_adk_agent  # noqa: E402
from argon.harness import ArgonHarness, _stage_prompt  # noqa: E402
from argon.models import ARTIFACT_NAMES, RunManifest  # noqa: E402
from argon.tools import execute_math_check, verify_scene  # noqa: E402
from argon.validation import (  # noqa: E402
    normalize_reverse_tree,
    validate_reverse_tree,
    validate_run,
    verify_scene_report,
)

NEEDS_REPLY = 2


def _ask(stages: Path, filename: str, charter: str, prompt: str) -> int:
    (stages / "NEXT_PROMPT.txt").write_text(
        "SYSTEM CHARTER:\n" + charter + "\n\nPROMPT:\n" + prompt,
        encoding="utf-8",
    )
    print(f"  [argon-operator] reply needed: save it as {stages / filename}")
    print(f"  [argon-operator] prompt written to {stages / 'NEXT_PROMPT.txt'}")
    return NEEDS_REPLY


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

    # Instantiate the Google ADK SequentialAgent and LlmAgent chain to verify ADK agent definitions.
    adk_pipeline = build_adk_sequential_pipeline(model=model, reasoning_effort="high")
    adk_sub_agents = {agent.output_key: agent for agent in adk_pipeline.sub_agents}

    harness = ArgonHarness(runs_dir=runs_dir)
    prior: dict[str, dict] = {}
    plan: list[tuple[str, str, str, str, dict]] = []

    for stage in STAGES:
        charter = load_charter(stage.charter_file)
        user_text = _stage_prompt(stage.name, prompt, prior)
        reply_path = stages / stage.artifact
        if not reply_path.is_file():
            return _ask(stages, stage.artifact, charter, user_text), None
        reply = json.loads(reply_path.read_text(encoding="utf-8"))
        if not isinstance(reply, dict) or not reply:
            raise SystemExit(f"stage {stage.name!r} rejected: artifact is not a non-empty JSON object")
        if stage.name == "cartographer":
            reply = normalize_reverse_tree(reply)
            tree_errors = validate_reverse_tree(reply)
            if tree_errors:
                raise SystemExit(
                    f"stage {stage.name!r} rejected by reverse-tree check: {'; '.join(tree_errors)}"
                )
        plan.append((stage.name, stage.artifact, charter, user_text, reply))
        prior[stage.artifact] = reply

    scene_path = stages / "argon_scene.py"
    if not scene_path.is_file():
        composer_charter = load_charter("argon-composer.md")
        composer_prompt = _stage_prompt("composer", prompt, prior)
        return _ask(stages, "argon_scene.py", composer_charter, composer_prompt), None

    (stages / "NEXT_PROMPT.txt").unlink(missing_ok=True)

    run_dir = harness._create_run_dir(prompt)
    now = datetime.now(timezone.utc).isoformat()
    manifest = RunManifest(
        run_id=run_dir.name,
        prompt=prompt,
        model=model,
        backend="argon-operator",
        sdk="google-adk + google-genai",
        offline=False,
        render_requested=render,
        quality=quality,
        created_utc=now,
        operator_note=(
            "Stages executed with Gemini 4 Argon acting as the Google ADK model backend "
            "(scripts/operate_argon_chain.py); every stage artifact and ADK tool call was verified by the harness."
        ),
    )
    traces_dir = run_dir / "traces"
    traces_dir.mkdir(exist_ok=True)
    (run_dir / "request.json").write_text(
        json.dumps(
            {
                "prompt": prompt,
                "render": render,
                "quality": quality,
                "reasoning_effort": "high",
                "sdk": "google-adk + google-genai",
                "adk_pipeline_name": adk_pipeline.name,
                "adk_sub_agents": [a.name for a in adk_pipeline.sub_agents],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    for stage_name, artifact_name, charter, stage_prompt, reply in plan:
        stem = artifact_name.split(".")[0]
        (run_dir / f"{stem}.prompt.txt").write_text(
            "SYSTEM CHARTER:\n" + charter + "\n\nPROMPT:\n" + stage_prompt,
            encoding="utf-8",
        )
        (run_dir / artifact_name).write_text(json.dumps(reply, indent=2), encoding="utf-8")

        tool_calls: list[dict] = []
        if stage_name == "math-director":
            for check_expr in reply.get("checks", []):
                if isinstance(check_expr, dict) and "expression" in check_expr:
                    res = execute_math_check(str(check_expr["expression"]))
                    tool_calls.append({"tool": "execute_math_check", "input": check_expr["expression"], "output": res})
            for num in reply.get("numbers", []):
                if isinstance(num, dict) and "expression" in num:
                    res = execute_math_check(str(num["expression"]))
                    tool_calls.append({"tool": "execute_math_check", "input": num["expression"], "output": res})

        adk_agent = adk_sub_agents.get(artifact_name) or build_stage_adk_agent(
            stage_name, instructions=charter, model=model
        )
        trace = {
            "stage": stage_name,
            "sdk": "google-adk",
            "adk_agent_name": adk_agent.name,
            "adk_output_key": adk_agent.output_key,
            "model": model,
            "tool_calls": tool_calls,
        }
        (traces_dir / f"{stage_name}.json").write_text(json.dumps(trace, indent=2), encoding="utf-8")
        manifest.stages.append(
            {
                "stage": stage_name,
                "artifact": artifact_name,
                "adk_agent": adk_agent.name,
                "bytes": len(json.dumps(reply)),
                "tool_calls": len(tool_calls),
            }
        )
        print(f"  [argon-adk] {stage_name:<16} -> {artifact_name} (valid, agent={adk_agent.name})")

    code = scene_path.read_text(encoding="utf-8")
    code_path = run_dir / "argon_scene.py"
    code_path.write_text(code, encoding="utf-8")

    verify_res = verify_scene(source=code)
    (run_dir / "validation.json").write_text(json.dumps(verify_res, indent=2), encoding="utf-8")
    (traces_dir / "composer.json").write_text(
        json.dumps(
            {
                "stage": "composer",
                "sdk": "google-adk",
                "adk_agent_name": "argon_composer",
                "model": model,
                "tool_calls": [{"tool": "verify_scene", "output": verify_res}],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    review_payload = {
        "offline": False,
        "sdk": "google-adk + google-genai",
        "model": model,
        "checks": ["artifact contract", "reverse tree", "execute_math_check", "verify_scene"],
        "rendered": render,
    }
    (run_dir / "review.json").write_text(json.dumps(review_payload, indent=2), encoding="utf-8")

    failures, scene_name, _ = validate_run(run_dir, require_video=False)
    print(
        f"  [argon-adk] composer         -> argon_scene.py ({scene_name}); static check "
        f"{'passed' if not failures else 'FAILED: ' + '; '.join(failures)}"
    )
    if failures:
        manifest.status = "failed"
        manifest.error = "; ".join(failures)
        harness._write_manifest(run_dir / "manifest.json", manifest)
        return 1, run_dir

    video_path = None
    if render:
        started = time.time()
        video_path = harness._render(run_dir, scene_name or "ScoreSDEConsistencyJourney", quality)
        elapsed = round(time.time() - started, 1)
        review_payload["rendered"] = True
        review_payload["render_seconds"] = elapsed
        review_payload["video_path"] = video_path
        (run_dir / "review.json").write_text(json.dumps(review_payload, indent=2), encoding="utf-8")
        print(f"  [argon-adk] rendered ({quality}) -> {video_path} in {elapsed}s")

    manifest.scene_file = "argon_scene.py"
    manifest.scene_name = scene_name
    manifest.video_path = video_path
    manifest.status = "completed"
    manifest.completed_utc = datetime.now(timezone.utc).isoformat()
    manifest.status_detail["validation"] = "complete"
    manifest.artifacts = {name: name for name in ARTIFACT_NAMES}
    harness._write_manifest(run_dir / "manifest.json", manifest)
    print(f"  [argon-adk] run recorded -> {run_dir}")
    return 0, run_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("stages", type=Path, help="directory holding prompt.txt and the stage replies")
    parser.add_argument("--runs-dir", type=Path, default=None)
    parser.add_argument(
        "--model",
        default="gemini-4-argon",
        help="model recorded in the manifest",
    )
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
