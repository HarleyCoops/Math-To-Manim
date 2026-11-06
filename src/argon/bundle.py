"""The Argon run bundle on disk: ``runs/argon/<timestamp>-<slug>/``.

One place knows the bundle layout (manifest, request, stage artifacts, scene,
validation, review, traces) and how to check a bundle against the stage
contract. The live harness, the offline rehearsal and the operator script all
write bundles through these functions.
"""

from __future__ import annotations

import os
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from argon.models import (
    MANIFEST_FILE,
    REQUEST_FILE,
    REVIEW_FILE,
    SCENE_FILE,
    SDK_NAME,
    TRACES_DIR,
    VALIDATION_FILE,
    RunManifest,
    StageCallResult,
)
from argon.stages import STAGE_ARTIFACTS, STAGES, Stage
from argon.validation import verify_scene_report

# Every file a completed bundle contains besides manifest/request/traces.
BUNDLE_FILES: tuple[str, ...] = STAGE_ARTIFACTS + (SCENE_FILE, VALIDATION_FILE, REVIEW_FILE)

# What validate_run checks; recorded in review.json.
VALIDATION_CHECKS: tuple[str, ...] = ("artifact contract", "reverse tree", "verify_scene")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_runs_dir() -> Path:
    """``$M2M_RUNS_DIR/argon``; else ``runs/argon`` in the source checkout this
    package runs from; else ``./runs/argon`` (installed wheel). Resolved at call time."""
    if os.getenv("M2M_RUNS_DIR"):
        return Path(os.environ["M2M_RUNS_DIR"]) / "argon"
    checkout = Path(__file__).resolve().parents[2]
    base = checkout if (checkout / "pyproject.toml").is_file() else Path.cwd()
    return base / "runs" / "argon"


def create_run_dir(runs_dir: Path, prompt: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    slug = re.sub(r"[^a-z0-9]+", "-", prompt.lower()).strip("-")[:48] or "film"
    candidate = runs_dir / f"{stamp}-{slug}"
    suffix = 1
    while candidate.exists():
        suffix += 1
        candidate = runs_dir / f"{stamp}-{slug}-{suffix}"
    candidate.mkdir(parents=True)
    (candidate / TRACES_DIR).mkdir()
    return candidate


def new_manifest(run_dir: Path, **fields) -> RunManifest:
    """A fresh ``running`` manifest for ``run_dir``; written once created."""
    manifest = RunManifest(
        run_id=run_dir.name,
        created_utc=utc_now(),
        artifacts={"validation": VALIDATION_FILE, "scene": SCENE_FILE},
        status_detail={"validation": "pending"},
        **fields,
    )
    write_manifest(run_dir, manifest)
    return manifest


def write_manifest(run_dir: Path, manifest: RunManifest) -> None:
    path = run_dir / MANIFEST_FILE
    temporary = path.with_suffix(".tmp")
    temporary.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    temporary.replace(path)


def complete_manifest(
    run_dir: Path,
    manifest: RunManifest,
    *,
    scene_name: str,
    video_path: str | None,
) -> RunManifest:
    manifest.scene_file = SCENE_FILE
    manifest.scene_name = scene_name
    manifest.video_path = video_path
    manifest.status = "completed"
    manifest.completed_utc = utc_now()
    manifest.status_detail["validation"] = "complete"
    manifest.artifacts = {name: name for name in BUNDLE_FILES}
    write_manifest(run_dir, manifest)
    return manifest


def fail_manifest(run_dir: Path, manifest: RunManifest, error: str) -> RunManifest:
    manifest.status = "failed"
    manifest.error = error
    manifest.completed_utc = utc_now()
    write_manifest(run_dir, manifest)
    return manifest


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_request(run_dir: Path, request: dict) -> None:
    _write_json(run_dir / REQUEST_FILE, request)


def write_artifact(run_dir: Path, stage: Stage, payload: dict) -> None:
    _write_json(run_dir / stage.artifact, payload)


def write_scene(run_dir: Path, source: str) -> None:
    (run_dir / SCENE_FILE).write_text(source, encoding="utf-8")


def read_scene(run_dir: Path) -> str:
    return (run_dir / SCENE_FILE).read_text(encoding="utf-8")


def write_trace(run_dir: Path, name: str, payload: dict) -> None:
    _write_json(run_dir / TRACES_DIR / f"{name}.json", payload)


def stage_trace(stage: Stage, result: StageCallResult, *, model: str, reasoning_effort: str) -> dict:
    return {
        "stage": stage.name,
        "sdk": "google-adk",
        "adk_agent_name": stage.agent_name,
        "model": model,
        "reasoning_effort": reasoning_effort,
        "tools_requested": stage.tool_names,
        "tool_calls": result.tool_calls,
        "thinking": result.thinking,
    }


def write_validation(run_dir: Path) -> dict:
    """Write validation.json from the scene file as it stands; returns the report."""
    report = verify_scene_report(read_scene(run_dir))
    _write_json(run_dir / VALIDATION_FILE, report)
    return report


def write_review(
    run_dir: Path,
    *,
    offline: bool,
    model: str,
    video_path: str | None = None,
    checks: tuple[str, ...] = VALIDATION_CHECKS,
    **extra,
) -> dict:
    review = {
        "offline": offline,
        "sdk": SDK_NAME,
        "model": model,
        "checks": list(checks),
        "rendered": video_path is not None,
    }
    if video_path is not None:
        review["video_path"] = video_path
    review.update(extra)
    _write_json(run_dir / REVIEW_FILE, review)
    return review


def validate_run(run_dir: Path) -> tuple[list[str], str | None]:
    """Check a bundle against the stage contract without writing anything.

    Returns ``(failures, scene_name)``; ``scene_name`` is set exactly when the
    scene file passed, so it is never None when ``failures`` is empty.
    """
    failures: list[str] = []
    for stage in STAGES:
        path = run_dir / stage.artifact
        if not path.is_file():
            failures.append(f"missing required artifact: {stage.artifact}")
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            failures.append(f"{stage.artifact}: invalid JSON ({exc})")
            continue
        if not isinstance(payload, dict) or not payload:
            failures.append(f"{stage.artifact}: expected a non-empty JSON object")
            continue
        if stage.check is not None:
            failures.extend(stage.check(stage.normalize(payload) if stage.normalize else payload))

    scene_path = run_dir / SCENE_FILE
    if not scene_path.is_file():
        failures.append(f"missing required artifact: {SCENE_FILE}")
        return failures, None
    report = verify_scene_report(scene_path.read_text(encoding="utf-8"))
    failures.extend(report["errors"])
    return failures, report["scene_name"]


# --- run ledger -------------------------------------------------------------


def run_dir_for(runs_dir: Path, run_id: str) -> Path:
    if Path(run_id).name != run_id:
        raise ValueError("run_id must be a single directory name")
    run_dir = runs_dir / run_id
    if not run_dir.is_dir():
        raise FileNotFoundError(f"unknown Argon run: {run_id}")
    return run_dir


def load_manifest(runs_dir: Path, run_id: str) -> RunManifest:
    manifest_path = run_dir_for(runs_dir, run_id) / MANIFEST_FILE
    if not manifest_path.is_file():
        raise FileNotFoundError(f"unknown Argon run: {run_id}")
    return RunManifest.model_validate(json.loads(manifest_path.read_text(encoding="utf-8")))


def list_manifests(runs_dir: Path, *, limit: int = 20) -> list[RunManifest]:
    if not runs_dir.exists():
        return []
    manifests: list[RunManifest] = []
    for path in sorted(runs_dir.glob(f"*/{MANIFEST_FILE}"), reverse=True):
        try:
            manifests.append(RunManifest.model_validate(json.loads(path.read_text(encoding="utf-8"))))
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        if len(manifests) >= limit:
            break
    return manifests
