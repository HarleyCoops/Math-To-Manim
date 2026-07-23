"""Resumable six-role orchestration for the Codex-native Sol pipeline."""

from __future__ import annotations

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from sol.agents import AGENT_STAGES, AgentStage, build_stage_prompt, stage_by_name
from sol.client import CodexCli
from sol.models import (
    ARTIFACT_NAMES,
    CodexRunResult,
    RunRequest,
    StageRecord,
    StageRunResult,
)


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
) -> str:
    payload = {
        "role": stage.name,
        "version": stage.version,
        "model": "gpt-5.6-sol",
        "reasoning_effort": stage.reasoning_effort,
        "request": request.model_dump(mode="json"),
        "upstream": dict(sorted(upstream_hashes.items())),
    }
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _record_relative(index: int, stage: AgentStage) -> str:
    return f"stages/{index:02d}-{stage.name}.json"


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
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"{stage.name}: invalid JSON artifact {name}") from exc
            if not isinstance(payload, dict) or not payload:
                raise RuntimeError(f"{stage.name}: {name} must contain a non-empty object")
        hashes[name] = _sha256(path)
    return hashes


def _downstream_names(from_stage: str) -> set[str]:
    stage_by_name(from_stage)
    selected = {from_stage}
    changed = True
    while changed:
        changed = False
        for stage in AGENT_STAGES:
            if stage.name not in selected and set(stage.dependencies) & selected:
                selected.add(stage.name)
                changed = True
    return selected


class StagedPipeline:
    def __init__(self, *, client: CodexCli):
        self.client = client

    def run(
        self,
        run_dir: Path,
        request: RunRequest,
        *,
        from_stage: str | None = None,
    ) -> CodexRunResult:
        run_dir = Path(run_dir)
        stages_dir = run_dir / "stages"
        stages_dir.mkdir(exist_ok=True)
        schema_path = stages_dir / "stage-result.schema.json"
        schema_path.write_text(
            json.dumps(StageRunResult.model_json_schema(), indent=2),
            encoding="utf-8",
        )
        forced = _downstream_names(from_stage) if from_stage else set()
        intent = self._run_stage(
            stage_by_name("intent"),
            1,
            run_dir,
            request,
            schema_path,
            forced,
            {},
        )

        def curriculum_lane() -> dict[str, str]:
            cartographer = self._run_stage(
                stage_by_name("cartographer"),
                2,
                run_dir,
                request,
                schema_path,
                forced,
                intent,
            )
            curriculum = self._run_stage(
                stage_by_name("curriculum"),
                3,
                run_dir,
                request,
                schema_path,
                forced,
                cartographer,
            )
            return {**cartographer, **curriculum}

        with ThreadPoolExecutor(max_workers=2, thread_name_prefix="sol-stage") as pool:
            curriculum_future = pool.submit(curriculum_lane)
            math_future = pool.submit(
                self._run_stage,
                stage_by_name("math-director"),
                4,
                run_dir,
                request,
                schema_path,
                forced,
                intent,
            )
            curriculum = curriculum_future.result()
            math_dossier = math_future.result()

        cinematographer = self._run_stage(
            stage_by_name("cinematographer"),
            5,
            run_dir,
            request,
            schema_path,
            forced,
            {**curriculum, **math_dossier},
        )
        self._run_stage(
            stage_by_name("scene-composer"),
            6,
            run_dir,
            request,
            schema_path,
            forced,
            cinematographer,
        )

        review_path = run_dir / "review.json"
        if not review_path.is_file():
            review_path.write_text(
                json.dumps(
                    {
                        "status": "awaiting_render" if request.render else "not_rendered",
                        "checks": ["six staged artifacts completed"],
                        "rendered": False,
                        "limitations": ["wrapper render has not run"],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
        return CodexRunResult(
            status="completed",
            scene_file="sol_scene.py",
            scene_name="",
            artifacts=list(ARTIFACT_NAMES),
            rendered=False,
            video_path=None,
            checks=["six durable Sol stages completed"],
            notes=[],
        )

    def _run_stage(
        self,
        stage: AgentStage,
        index: int,
        run_dir: Path,
        request: RunRequest,
        schema_path: Path,
        forced: set[str],
        upstream_hashes: dict[str, str],
    ) -> dict[str, str]:
        input_hash = stage_input_hash(stage, request, upstream_hashes)
        record_path = run_dir / _record_relative(index, stage)
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

        stages_dir = run_dir / "stages"
        stem = f"{index:02d}-{stage.name}"
        trace_path = stages_dir / f"{stem}.jsonl"
        result_path = stages_dir / f"{stem}-result.json"
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
                build_stage_prompt(stage, request, run_dir=run_dir),
                cwd=run_dir,
                schema_path=schema_path,
                output_path=result_path,
                trace_path=trace_path,
                event_sink=consume_event,
                session_id=record.thread_id if previous else None,
                reasoning_effort=stage.reasoning_effort,
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


def write_offline_stage_records(run_dir: Path, request: RunRequest) -> list[str]:
    stages_dir = run_dir / "stages"
    stages_dir.mkdir(exist_ok=True)
    artifact_hashes: dict[str, str] = {}
    records: list[str] = []
    for index, stage in enumerate(AGENT_STAGES, start=1):
        upstream = {
            name: artifact_hashes[name]
            for dependency in stage.dependencies
            for name in stage_by_name(dependency).artifacts
        }
        hashes = _validate_artifacts(run_dir, stage)
        relative = _record_relative(index, stage)
        record = StageRecord(
            name=stage.name,
            status="completed",
            input_hash=stage_input_hash(stage, request, upstream),
            artifact_hashes=hashes,
            thread_id=None,
            trace_path=f"stages/{index:02d}-{stage.name}.jsonl",
            result_path=f"stages/{index:02d}-{stage.name}-result.json",
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
        _write_json_atomic(run_dir / relative, record.model_dump_json(indent=2))
        artifact_hashes.update(hashes)
        records.append(relative)
    return records
