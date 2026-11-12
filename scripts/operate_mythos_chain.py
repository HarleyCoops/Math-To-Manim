"""Operate the Mythos six-agent chain with yourself (or any session) as the model.

The Mythos harness normally sends each stage's prompt to a CLI backend. This
script lets an operator, for example a Claude session, answer the stages
instead, while the harness's own checks judge every answer:

* each stage receives exactly the prompt the harness builds: the stage charter,
  the previous stage's JSON and the JSON contract, with the Cinematic Charter as
  system text. The prompt is saved as ``NN_*.prompt.txt`` in the run directory;
* each reply must pass ``validate_stage_artifact``;
* the scene must pass the harness's static checks (AST, LaTeX fragments,
  charter lint), and the run manifest is written with the versioned schema;
* ``--render`` renders through the harness's pinned-path renderer.

Workflow: put the production prompt in ``<stages>/prompt.txt`` and run the
script. It stops at the first stage that has no reply, writes that stage's full
prompt to ``<stages>/NEXT_PROMPT.txt`` and exits with status 2. Save the reply
as the named artifact (``01_intent.json`` ... ``06_scene_spec.json``, then
``mythos_scene.py`` for codegen) and run it again. When every reply is present
and valid it records the run and exits 0.

    python scripts/operate_mythos_chain.py path/to/stages
    python scripts/operate_mythos_chain.py path/to/stages --render -q l

"Every Orbit Is a Great Circle" (docs/showcase/every-orbit-great-circle/) was
made this way.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from mythos.charter import CINEMATIC_CHARTER  # noqa: E402
from mythos.harness import (  # noqa: E402
    MythosHarness,
    check_scene,
    codegen_prompt,
    new_manifest,
    record_check,
    stage_prompt,
)
from mythos.layout import SCENE_FILE, create_run_dir, write_manifest  # noqa: E402
from mythos.scene_checks import find_scene_class  # noqa: E402
from mythos.settings import default_runs_dir  # noqa: E402
from mythos.stages import STAGES, validate_stage_artifact  # noqa: E402

NEEDS_REPLY = 2


def _with_system_extra(prompt: str) -> str:
    return "SYSTEM EXTRA:\n" + CINEMATIC_CHARTER + "\n\nPROMPT:\n" + prompt


def _ask(stages: Path, filename: str, prompt: str) -> int:
    (stages / "NEXT_PROMPT.txt").write_text(_with_system_extra(prompt), encoding="utf-8")
    print(f"  [operator] reply needed: save it as {stages / filename}")
    print(f"  [operator] prompt written to {stages / 'NEXT_PROMPT.txt'}")
    return NEEDS_REPLY


def operate(stages: Path, *, runs_dir: Path | None = None, model: str = "operator session",
            render: bool = False, quality: str = "l") -> tuple[int, Path | None]:
    stages = Path(stages).resolve()
    prompt_file = stages / "prompt.txt"
    if not prompt_file.is_file():
        raise SystemExit(f"missing production prompt: {prompt_file}")
    prompt = prompt_file.read_text(encoding="utf-8").replace(chr(0xFEFF), "").strip()
    runs_dir = Path(runs_dir) if runs_dir else default_runs_dir()

    # Replay the chain up to the first missing reply before creating a run.
    artifact: dict = {"user_prompt": prompt}
    plan = []
    for stage in STAGES:
        prompt_text = stage_prompt(stage, artifact)
        reply_path = stages / stage.artifact
        if not reply_path.is_file():
            return _ask(stages, stage.artifact, prompt_text), None
        reply = json.loads(reply_path.read_text(encoding="utf-8"))
        problem = validate_stage_artifact(stage.slug, reply)
        if problem:
            raise SystemExit(f"stage {stage.slug!r} rejected by the harness: {problem}")
        plan.append((stage, prompt_text, reply))
        artifact = reply
    dossier = {stage.artifact: reply for stage, _, reply in plan}
    scene_path = stages / SCENE_FILE
    if not scene_path.is_file():
        return _ask(stages, SCENE_FILE, codegen_prompt(dossier)), None
    (stages / "NEXT_PROMPT.txt").unlink(missing_ok=True)

    run_dir = create_run_dir(runs_dir, prompt)
    manifest = new_manifest(run_dir, prompt=prompt, model=model, command="operator",
                            offline=False)
    manifest["operator_note"] = (
        "Stages answered by an operator acting as the model backend "
        "(scripts/operate_mythos_chain.py); every reply was checked by the harness.")
    for stage, prompt_text, reply in plan:
        (run_dir / f"{stage.stem}.prompt.txt").write_text(
            _with_system_extra(prompt_text), encoding="utf-8")
        (run_dir / stage.artifact).write_text(json.dumps(reply, indent=2), encoding="utf-8")
        manifest["stages"].append({"stage": stage.slug, "artifact": stage.artifact,
                                   "bytes": len(json.dumps(reply))})
        print(f"  [mythos] {stage.slug:<16} -> {stage.artifact} (valid)")
    (run_dir / "07_codegen.prompt.txt").write_text(codegen_prompt(dossier), encoding="utf-8")
    code = scene_path.read_text(encoding="utf-8")
    code_path = run_dir / SCENE_FILE
    code_path.write_text(code, encoding="utf-8")
    scene_name = find_scene_class(code)
    manifest["stages"].append({"stage": "codegen", "artifact": SCENE_FILE})
    check = check_scene(code_path, prompt=prompt)
    record_check(run_dir, manifest, check)
    write_manifest(run_dir, manifest)
    print(f"  [mythos] codegen          -> {SCENE_FILE} ({scene_name}); static check "
          f"{'passed' if check.ok else 'FAILED: ' + str(check.failure)}")
    if not check.ok:
        return 1, run_dir
    if render:
        harness = MythosHarness(command="operator", model=model, runs_dir=runs_dir)
        started = time.time()
        result = harness.render_workspace(run_dir, scene_name, quality)
        rc, out, manifest = result["exit_code"], result["output"], result["manifest"]
        manifest["renders"][-1].update(
            {"quality": quality, "seconds": round(time.time() - started, 1)})
        write_manifest(run_dir, manifest)
        print(out[-2000:])
        if rc != 0:
            return rc, run_dir
    print(f"  [mythos] run recorded -> {run_dir}")
    return 0, run_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("stages", type=Path, help="directory holding prompt.txt and the replies")
    parser.add_argument("--runs-dir", type=Path, default=None,
                        help="run ledger (default: M2M_RUNS_DIR or ./runs, under mythos/)")
    parser.add_argument("--model", default="operator session",
                        help="recorded in the manifest, e.g. the model the session runs on")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("-q", "--quality", default="l", choices=list("lmhpk"))
    args = parser.parse_args(argv)
    rc, _ = operate(args.stages, runs_dir=args.runs_dir, model=args.model,
                    render=args.render, quality=args.quality)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
