"""The Studio run: a question in, ``film.mp4`` out, as an explicit state machine.

    run_film("What is altermagnetism?")           # agents write the film
    run_film("rehearsal", offline=True)           # a fixed film, no model calls
    run_film("my film", spec_path="spec.json")    # render a SceneSpec file

Stages, in order: ``directing`` -> ``speccing`` -> ``rendering`` -> ``done``.
Code owns the order. An agent owns the content of one stage. The manifest in
the run folder records ``status.run`` (running, completed, failed),
``status.stage`` (the stage running now, or the stage that failed),
``status.outcome`` and the state of every shot. It is rewritten after every
change, so a reader always sees where the run is.

Outcomes: ``film_ready`` (every shot is in the film), ``film_partial`` (the
film was built without the shots that failed), ``failed`` (no film).
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from studio import __version__
from studio.authoring import direct, write_spec
from studio.doctor import Runner, run_command
from studio.film import build_film
from studio.runtime import AgentRuntime, get_runtime
from studio.settings import default_runs_dir
from studio.spec.models import SceneSpec, load_spec

STAGES = ("directing", "speccing", "rendering", "done")
OFFLINE_SPEC = Path(__file__).resolve().parent / "examples" / "offline_film.json"
MANIFEST = "manifest.json"


def create_run_dir(question: str) -> Path:
    slug = re.sub(r"[^a-z0-9]+", "-", question.lower()).strip("-")[:48] or "run"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_dir = default_runs_dir() / f"{stamp}-{slug}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def write_manifest(run_dir: Path, manifest: dict[str, Any]) -> None:
    """Atomic: a reader that polls the run folder never sees half a file."""
    payload = json.dumps(manifest, indent=2)
    target, tmp = run_dir / MANIFEST, run_dir / f".{MANIFEST}.tmp"
    tmp.write_text(payload, encoding="utf-8")
    for attempt in range(8):
        try:
            os.replace(tmp, target)
            return
        except PermissionError:  # Windows: a reader holds the file open
            time.sleep(0.02 * (attempt + 1))
    target.write_text(payload, encoding="utf-8")


def run_film(question: str, *, offline: bool = False, spec_path: Path | str | None = None,
             runtime: AgentRuntime | None = None, runner: Runner = run_command,
             samples: int = 32, log: Callable[[str], None] = print) -> dict[str, Any]:
    """Run every stage and return the final manifest. Raises nothing for a failed run."""
    question = question.strip()
    if not question:
        raise ValueError("question must not be empty")
    run_dir = create_run_dir(question)
    manifest: dict[str, Any] = {
        "studio": __version__,
        "run_id": run_dir.name,
        "question": question,
        "mode": "spec" if spec_path else ("offline" if offline else "agents"),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": {"run": "running", "stage": STAGES[0], "outcome": None},
        "stages": [],
        "shots": {},
        "film": None,
    }

    def enter(stage: str) -> float:
        manifest["status"]["stage"] = stage
        write_manifest(run_dir, manifest)
        log(f"[studio] {stage}")
        return time.perf_counter()

    def leave(stage: str, started: float, **facts: Any) -> None:
        manifest["stages"].append(
            {"stage": stage, "seconds": round(time.perf_counter() - started, 1), **facts})

    def on_shot(shot_id: str, state: dict[str, Any]) -> None:
        manifest["shots"][shot_id] = state
        write_manifest(run_dir, manifest)

    try:
        started = enter("directing")
        if spec_path or offline:
            brief: dict[str, Any] = {"skipped": "no agents in this mode"}
        else:
            runtime = runtime or get_runtime()
            manifest["runtime"] = runtime.name
            brief = direct(runtime, question, run_dir, log).model_dump()
        (run_dir / "brief.json").write_text(json.dumps(brief, indent=2), encoding="utf-8")
        leave("directing", started, artifact="brief.json")

        started = enter("speccing")
        if spec_path or offline:
            spec = load_spec(spec_path or OFFLINE_SPEC)
        else:
            from studio.authoring import Brief

            spec = write_spec(runtime, question, Brief.model_validate(brief), run_dir, log)
        (run_dir / "scenespec.json").write_text(
            json.dumps(spec.model_dump(), indent=2), encoding="utf-8")
        manifest["title"] = spec.title
        manifest["planned_seconds"] = round(spec.duration_s(), 2)
        leave("speccing", started, artifact="scenespec.json", shots=len(spec.shots))

        started = enter("rendering")
        result = build_film(spec, run_dir, samples=samples, runner=runner,
                            on_shot=on_shot, log=log)
        manifest["shots"] = result["shots"]
        manifest["film"] = result["film"]
        manifest["contact_sheet"] = result["contact_sheet"]
        manifest["film_seconds"] = result["seconds"]
        if result.get("error"):
            manifest["error"] = result["error"]
        leave("rendering", started,
              accepted=sum(1 for s in result["shots"].values() if s["state"] == "accepted"),
              failed=sum(1 for s in result["shots"].values() if s["state"] == "failed"))
        outcome = result["outcome"]
        manifest["status"].update(
            run="failed" if outcome == "failed" else "completed",
            outcome=outcome)
        if outcome != "failed":
            manifest["status"]["stage"] = "done"
            manifest["completed_utc"] = datetime.now(timezone.utc).isoformat()
    except BaseException as exc:
        # status.stage keeps the stage that failed.
        manifest["status"].update(run="failed", outcome="failed")
        manifest["error"] = f"{type(exc).__name__}: {exc}"[:2000]
        manifest["failed_utc"] = datetime.now(timezone.utc).isoformat()
        write_manifest(run_dir, manifest)
        log(f"[studio] FAILED at {manifest['status']['stage']}: {manifest['error'][:300]}")
        if not isinstance(exc, Exception):
            raise  # Ctrl-C and exit requests still stop the process
        return manifest
    write_manifest(run_dir, manifest)
    log(f"[studio] {manifest['status']['outcome']} -> {run_dir}")
    return manifest


def read_manifest(run_id: str) -> dict[str, Any]:
    run_dir = (default_runs_dir() / run_id).resolve()
    if default_runs_dir().resolve() not in run_dir.parents:
        raise ValueError(f"invalid run id {run_id!r}")
    return json.loads((run_dir / MANIFEST).read_text(encoding="utf-8"))


def list_runs(limit: int = 20) -> list[dict[str, Any]]:
    root = default_runs_dir()
    runs = []
    for path in sorted(root.glob(f"*/{MANIFEST}"), reverse=True)[:limit]:
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        runs.append({"run_id": manifest.get("run_id"), "question": manifest.get("question"),
                     "status": manifest.get("status"), "film": manifest.get("film")})
    return runs
