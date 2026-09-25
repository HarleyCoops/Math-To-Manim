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
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mythos.charter import CINEMATIC_CHARTER, JSON_CONTRACT, find_scene_class  # noqa: E402
from mythos.harness import STAGES, MythosHarness, validate_stage_artifact  # noqa: E402
from mythos.manifest_schema import manifest_template, validation_template  # noqa: E402
from mythos.scene_checks import write_json  # noqa: E402

NEEDS_REPLY = 2


def codegen_prompt(dossier: dict) -> str:
    """The prompt the harness sends for codegen (see MythosHarness._codegen)."""
    return (
        "You are the Mythos scene composer's hands: write the film.\n"
        "Using the full dossier below (intent through scene spec), write ONE\n"
        "complete, runnable Manim Community Edition Python file that\n"
        "implements the shot list with the full Cinematic Charter — headlines\n"
        "before symbols, camera zooms into terms, plain-language captions,\n"
        "Mythos palette. The file must be self-contained (inline any helpers),\n"
        "import `from manim import *`, and define exactly one ThreeDScene\n"
        "subclass. Respond with exactly one fenced python block and nothing\n"
        "else.\n\nDOSSIER JSON:\n" + json.dumps(dossier, indent=2)
    )


def _ask(stages: Path, filename: str, prompt: str) -> int:
    (stages / "NEXT_PROMPT.txt").write_text(
        "SYSTEM EXTRA:\n" + CINEMATIC_CHARTER + "\n\nPROMPT:\n" + prompt, encoding="utf-8")
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
    harness = MythosHarness(command="operator", model=model,
                            runs_dir=runs_dir or REPO_ROOT / "runs" / "mythos")

    # Replay the chain up to the first missing reply before creating a run.
    artifact: dict = {"user_prompt": prompt}
    plan = []
    for slug, agent_file, artifact_name in STAGES:
        charter = harness.load_charter(agent_file)
        stage_prompt = (f"{charter}\n\nINPUT ARTIFACT JSON:\n{json.dumps(artifact, indent=2)}"
                        f"{JSON_CONTRACT}")
        reply_path = stages / artifact_name
        if not reply_path.is_file():
            return _ask(stages, artifact_name, stage_prompt), None
        reply = json.loads(reply_path.read_text(encoding="utf-8"))
        problem = validate_stage_artifact(slug, reply)
        if problem:
            raise SystemExit(f"stage {slug!r} rejected by the harness: {problem}")
        plan.append((slug, artifact_name, stage_prompt, reply))
        artifact = reply
    dossier = {name: reply for _, name, _, reply in plan}
    scene_path = stages / "mythos_scene.py"
    if not scene_path.is_file():
        return _ask(stages, "mythos_scene.py", codegen_prompt(dossier)), None
    (stages / "NEXT_PROMPT.txt").unlink(missing_ok=True)

    run_dir = harness._create_run_dir(prompt)
    manifest = manifest_template(run_id=run_dir.name, prompt=prompt, model=harness.model,
                                 command="operator", offline=False,
                                 created_utc=datetime.now(timezone.utc).isoformat())
    manifest["operator_note"] = (
        "Stages answered by an operator acting as the model backend "
        "(scripts/operate_mythos_chain.py); every reply was checked by the harness.")
    write_json(run_dir / "validation.json", validation_template())
    for slug, artifact_name, stage_prompt, reply in plan:
        stem = artifact_name.split(".")[0]
        (run_dir / f"{stem}.prompt.txt").write_text(
            "SYSTEM EXTRA:\n" + CINEMATIC_CHARTER + "\n\nPROMPT:\n" + stage_prompt, encoding="utf-8")
        (run_dir / artifact_name).write_text(json.dumps(reply, indent=2), encoding="utf-8")
        manifest["stages"].append({"stage": slug, "artifact": artifact_name,
                                   "bytes": len(json.dumps(reply))})
        print(f"  [mythos] {slug:<16} -> {artifact_name} (valid)")
    (run_dir / "07_codegen.prompt.txt").write_text(codegen_prompt(dossier), encoding="utf-8")
    code = scene_path.read_text(encoding="utf-8")
    code_path = run_dir / "mythos_scene.py"
    code_path.write_text(code, encoding="utf-8")
    scene_name = find_scene_class(code)
    manifest["stages"].append({"stage": "codegen", "artifact": "mythos_scene.py"})
    ok, failure = harness._verify(code_path, prompt=prompt)
    harness._record_validation(run_dir, manifest, code_path, ok, failure)
    harness._write_manifest(run_dir, manifest)
    print(f"  [mythos] codegen          -> mythos_scene.py ({scene_name}); static check "
          f"{'passed' if ok else 'FAILED: ' + str(failure)}")
    if not ok:
        return 1, run_dir
    if render:
        started = time.time()
        rc, out = harness._render(code_path, scene_name, quality)
        manifest.setdefault("renders", []).append(
            {"quality": quality, "exit_code": rc, "seconds": round(time.time() - started, 1)})
        manifest.setdefault("status", {})["render"] = "complete" if rc == 0 else "failed"
        harness._write_manifest(run_dir, manifest)
        print(out[-2000:])
        if rc != 0:
            return rc, run_dir
    print(f"  [mythos] run recorded -> {run_dir}")
    return 0, run_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("stages", type=Path, help="directory holding prompt.txt and the replies")
    parser.add_argument("--runs-dir", type=Path, default=None)
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
