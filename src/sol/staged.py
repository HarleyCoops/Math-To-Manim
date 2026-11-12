"""Resumable six-role orchestration for the Codex-native Sol pipeline.

The scheduler is driven entirely by ``AGENT_STAGES``: a stage starts as soon
as its dependencies have completed, independent stages run in parallel, and a
stage is skipped when its input hash and artifacts match its saved record.
"""

from __future__ import annotations

import hashlib
import json
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from datetime import datetime, timezone
from pathlib import Path

from sol.agents import (
    AGENT_STAGES,
    AgentStage,
    build_stage_prompt,
    downstream_of,
    stage_by_name,
    stage_effort,
    stage_index,
    stage_record_path,
    upstream_artifacts,
)
from sol.client import CodexCli
from sol.layout import REVIEW_FILE, STAGE_RESULT_SCHEMA_FILE, STAGES_DIR
from sol.models import RunRequest, StageRecord, StageRunResult
from sol.validation import json_object_failure

REVIEW_STAGE = "cinematographer"
REVIEW_REPAIR_STAGE = "scene-composer"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json_atomic(path: Path, payload: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(path)


def stage_input_hash(
    stage: AgentStage,
    request: RunRequest,
    upstream_hashes: dict[str, str],
    model: str,
) -> str:
    payload = {
        "role": stage.name,
        "charter": stage.charter,
        "model": model,
        "reasoning_effort": stage_effort(stage, request),
        "request": request.model_dump(mode="json"),
        "upstream": dict(sorted(upstream_hashes.items())),
    }
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _load_record(path: Path) -> StageRecord | None:
    if not path.is_file():
        return None
    try:
        return StageRecord.model_validate_json(path.read_text(encoding="utf-8"))
    except ValueError:
        return None


def _validate_artifacts(run_dir: Path, stage: AgentStage) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for name in stage.artifacts:
        path = run_dir / name
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"{stage.name}: missing or empty artifact {name}")
        if name.endswith(".json"):
            failure = json_object_failure(path)
            if failure:
                raise RuntimeError(f"{stage.name}: {failure}")
        hashes[name] = _sha256(path)
    return hashes


def _prepare_stages_dir(run_dir: Path) -> Path:
    """Create ``stages/`` and return the shared structured-output schema path."""
    stages_dir = run_dir / STAGES_DIR
    stages_dir.mkdir(exist_ok=True)
    schema_path = stages_dir / STAGE_RESULT_SCHEMA_FILE
    schema_path.write_text(
        json.dumps(StageRunResult.model_json_schema(), indent=2),
        encoding="utf-8",
    )
    return schema_path


class StagedPipeline:
    def __init__(self, *, client: CodexCli):
        self.client = client

    def run(
        self,
        run_dir: Path,
        request: RunRequest,
        *,
        from_stage: str | None = None,
        feedback: dict[str, str] | None = None,
    ) -> list[str]:
        """Run every stage in dependency order; return the stage record paths."""
        run_dir = Path(run_dir)
        schema_path = _prepare_stages_dir(run_dir)
        forced = downstream_of(from_stage) if from_stage else set()
        hashes: dict[str, str] = {}
        done: set[str] = set()
        running: dict[Future, AgentStage] = {}
        with ThreadPoolExecutor(
            max_workers=len(AGENT_STAGES), thread_name_prefix="sol-stage"
        ) as pool:
            while len(done) < len(AGENT_STAGES):
                active = {stage.name for stage in running.values()}
                for stage in AGENT_STAGES:
                    if stage.name in done or stage.name in active:
                        continue
                    if not set(stage.dependencies) <= done:
                        continue
                    upstream = {name: hashes[name] for name in upstream_artifacts(stage)}
                    future = pool.submit(
                        self._run_stage, stage, run_dir, request, schema_path,
                        forced, upstream, feedback,
                    )
                    running[future] = stage
                finished, _ = wait(running, return_when=FIRST_COMPLETED)
                for future in finished:
                    stage = running.pop(future)
                    try:
                        hashes.update(future.result())
                    except Exception:
                        for pending in running:
                            pending.cancel()
                        raise
                    done.add(stage.name)
        return [stage_record_path(stage) for stage in AGENT_STAGES]

    def review_render(
        self,
        run_dir: Path,
        request: RunRequest,
        *,
        evidence_paths: list[Path],
    ) -> dict:
        """Ask the saved cinematographer session to judge the rendered frames."""
        run_dir = Path(run_dir)
        stage = stage_by_name(REVIEW_STAGE)
        record_path = run_dir / stage_record_path(stage)
        record = _load_record(record_path)
        if record is None or not record.thread_id:
            raise RuntimeError(f"{REVIEW_STAGE} thread is unavailable for render review")
        attempt = len(record.followups) + 1
        stages_dir = run_dir / STAGES_DIR
        schema_path = stages_dir / STAGE_RESULT_SCHEMA_FILE
        stem = f"{stage_index(stage):02d}-{stage.name}-review-{attempt}"
        trace_path = stages_dir / f"{stem}.jsonl"
        result_path = stages_dir / f"{stem}-result.json"
        review_path = run_dir / REVIEW_FILE
        # Never leave a previous verdict where this review's result is read back.
        review_path.unlink(missing_ok=True)
        evidence = "\n".join(
            f"- {path.relative_to(run_dir)}" for path in evidence_paths
        )
        prompt = f"""This is a render-review continuation of your saved
{REVIEW_STAGE} role in the staged GPT-6 Astra film pipeline.

Inspect these representative images from the rendered film:
{evidence}

Compare them against the original request:
<request>
{request.prompt}
</request>

Check mathematical fidelity, off-white continuity, true 3D depth and parallax,
camera framing, whitespace, complete readable LaTeX, text density, clipping,
and whether the final tableau works at README scale. Write only {REVIEW_FILE} as
a non-empty JSON object with exactly these top-level fields:
- status: "approved" or "needs_repair"
- defects: a JSON array of concrete timestamp/frame-linked defects
- observations: a JSON array of visual findings
- evidence: a JSON array of inspected relative paths

Do not modify the scene, shot list, or any other artifact. Finish with the
strict structured stage summary required by the supplied schema, using role
"{REVIEW_STAGE}" and artifacts ["{REVIEW_FILE}"].
"""
        followup = {
            "kind": "render-review",
            "status": "running",
            "trace_path": str(trace_path.relative_to(run_dir)),
            "result_path": str(result_path.relative_to(run_dir)),
            "started_utc": _now(),
        }
        record.followups.append(followup)
        record.attempts += 1
        _write_json_atomic(record_path, record.model_dump_json(indent=2))

        def consume_event(event: dict) -> None:
            record.event_count += 1
            if event.get("type") == "thread.started" and event.get("thread_id"):
                record.thread_id = str(event["thread_id"])
            _write_json_atomic(record_path, record.model_dump_json(indent=2))

        try:
            result = self.client.run(
                prompt,
                cwd=run_dir,
                schema_path=schema_path,
                output_path=result_path,
                trace_path=trace_path,
                event_sink=consume_event,
                session_id=record.thread_id,
                reasoning_effort=stage_effort(stage, request),
                result_model=StageRunResult,
                image_paths=evidence_paths,
            )
            if (
                not isinstance(result, StageRunResult)
                or result.status != "completed"
                or result.role != REVIEW_STAGE
                or result.artifacts != [REVIEW_FILE]
            ):
                raise RuntimeError(f"{REVIEW_STAGE} returned an invalid review summary")
            if not review_path.is_file():
                raise RuntimeError(f"{REVIEW_STAGE} did not write {REVIEW_FILE}")
            review = json.loads(review_path.read_text(encoding="utf-8"))
            if not isinstance(review, dict) or review.get("status") not in {
                "approved",
                "needs_repair",
            }:
                raise RuntimeError(f"{REVIEW_FILE} has an invalid status")
            if not isinstance(review.get("defects"), list):
                raise RuntimeError(f"{REVIEW_FILE} defects must be a list")
            review = {
                **review,
                "evaluator": REVIEW_STAGE,
                "repair_stage": REVIEW_REPAIR_STAGE,
                "observations": list(review.get("observations") or []),
                "evidence": list(review.get("evidence") or []),
            }
            review_path.write_text(json.dumps(review, indent=2), encoding="utf-8")
            followup["status"] = "completed"
            followup["completed_utc"] = _now()
        except Exception as exc:
            followup["status"] = "failed"
            followup["completed_utc"] = _now()
            followup["error"] = f"{type(exc).__name__}: {exc}"
            _write_json_atomic(record_path, record.model_dump_json(indent=2))
            raise
        _write_json_atomic(record_path, record.model_dump_json(indent=2))
        return review

    def _run_stage(
        self,
        stage: AgentStage,
        run_dir: Path,
        request: RunRequest,
        schema_path: Path,
        forced: set[str],
        upstream_hashes: dict[str, str],
        feedback: dict[str, str] | None,
    ) -> dict[str, str]:
        input_hash = stage_input_hash(stage, request, upstream_hashes, self.client.model)
        record_path = run_dir / stage_record_path(stage)
        previous = _load_record(record_path)
        cached = (
            stage.name not in forced
            and previous is not None
            and previous.status in {"completed", "cached"}
            and previous.input_hash == input_hash
        )
        if cached:
            try:
                current_hashes = _validate_artifacts(run_dir, stage)
            except RuntimeError:
                cached = False
            else:
                cached = current_hashes == previous.artifact_hashes
        if cached and previous is not None:
            previous.status = "cached"
            _write_json_atomic(record_path, previous.model_dump_json(indent=2))
            return previous.artifact_hashes

        stem = f"{stage_index(stage):02d}-{stage.name}"
        trace_path = run_dir / STAGES_DIR / f"{stem}.jsonl"
        result_path = run_dir / STAGES_DIR / f"{stem}-result.json"
        record = StageRecord(
            name=stage.name,
            status="running",
            input_hash=input_hash,
            thread_id=previous.thread_id if previous else None,
            trace_path=str(trace_path.relative_to(run_dir)),
            result_path=str(result_path.relative_to(run_dir)),
            event_count=0,
            attempts=(previous.attempts if previous else 0) + 1,
            started_utc=_now(),
        )
        _write_json_atomic(record_path, record.model_dump_json(indent=2))

        def consume_event(event: dict) -> None:
            record.event_count += 1
            if event.get("type") == "thread.started" and event.get("thread_id"):
                record.thread_id = str(event["thread_id"])
            _write_json_atomic(record_path, record.model_dump_json(indent=2))

        try:
            result = self.client.run(
                build_stage_prompt(
                    stage,
                    request,
                    run_dir=run_dir,
                    feedback=(feedback or {}).get(stage.name),
                ),
                cwd=run_dir,
                schema_path=schema_path,
                output_path=result_path,
                trace_path=trace_path,
                event_sink=consume_event,
                session_id=record.thread_id,
                reasoning_effort=stage_effort(stage, request),
                result_model=StageRunResult,
            )
            if not isinstance(result, StageRunResult):
                raise RuntimeError(f"{stage.name}: unexpected structured result type")
            if result.status != "completed" or result.role != stage.name:
                raise RuntimeError(f"{stage.name}: stage reported {result.status}")
            if set(result.artifacts) != set(stage.artifacts):
                raise RuntimeError(f"{stage.name}: structured artifact list mismatch")
            record.artifact_hashes = _validate_artifacts(run_dir, stage)
            record.status = "completed"
            record.completed_utc = _now()
        except Exception as exc:
            record.status = "failed"
            record.error = f"{type(exc).__name__}: {exc}"
            record.completed_utc = _now()
            _write_json_atomic(record_path, record.model_dump_json(indent=2))
            raise
        _write_json_atomic(record_path, record.model_dump_json(indent=2))
        return record.artifact_hashes


def write_offline_stage_records(run_dir: Path, request: RunRequest, model: str) -> list[str]:
    """Record every stage as completed from the artifacts already on disk."""
    _prepare_stages_dir(run_dir)
    artifact_hashes: dict[str, str] = {}
    records: list[str] = []
    for stage in AGENT_STAGES:
        upstream = {name: artifact_hashes[name] for name in upstream_artifacts(stage)}
        hashes = _validate_artifacts(run_dir, stage)
        stem = f"{stage_index(stage):02d}-{stage.name}"
        record = StageRecord(
            name=stage.name,
            status="completed",
            input_hash=stage_input_hash(stage, request, upstream, model),
            artifact_hashes=hashes,
            thread_id=None,
            trace_path=f"{STAGES_DIR}/{stem}.jsonl",
            result_path=f"{STAGES_DIR}/{stem}-result.json",
            completed_utc=_now(),
        )
        (run_dir / record.trace_path).touch()
        result = StageRunResult(
            status="completed",
            role=stage.name,
            artifacts=list(stage.artifacts),
            summary="offline deterministic rehearsal",
            checks=["artifact present"],
            notes=["No Codex call was made"],
        )
        (run_dir / record.result_path).write_text(
            result.model_dump_json(indent=2),
            encoding="utf-8",
        )
        relative = stage_record_path(stage)
        _write_json_atomic(run_dir / relative, record.model_dump_json(indent=2))
        artifact_hashes.update(hashes)
        records.append(relative)
    return records
