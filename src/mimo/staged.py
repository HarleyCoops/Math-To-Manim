"""Tool-calling stage orchestration for the MiMo 2.6 pipeline.

Stages are scheduled from the stage table's dependencies: every stage runs in
its own worker and waits for the stages it depends on, so independent lanes
(cartographer -> curriculum, math-director) overlap without any hand-wired
ordering. A stage whose inputs and artifacts are unchanged since its last
completed record is skipped ("cached") unless it is forced via ``from_stage``.
"""

from __future__ import annotations

import hashlib
import json
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from mimo.agents import AGENT_STAGES, AgentStage, build_stage_prompt, stage_by_name, stages_from
from mimo.models import STAGES_DIR, PipelineResult, RunRequest, StageRecord, StageRunResult
from mimo.tools import ToolContext
from mimo.validation import artifact_failures


class StageClient(Protocol):
    """What the pipeline needs from a model client (``MimoClient`` or a test fake)."""

    model: str

    def run_stage(
        self,
        *,
        stage_name: str,
        prompt: str,
        tools: tuple[dict, ...],
        ctx: ToolContext,
        reasoning_effort: str,
    ) -> StageRunResult: ...


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json_atomic(path: Path, payload: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(path)


def _artifact_hashes(run_dir: Path, stage: AgentStage) -> dict[str, str]:
    """Hashes of the stage's artifacts; raises if any is missing or malformed."""
    failures = artifact_failures(run_dir, stage.artifacts)
    if failures:
        raise RuntimeError(f"{stage.name}: " + "; ".join(failures))
    return {name: _sha256_file(run_dir / name) for name in stage.artifacts}


def _record_stem(stage: AgentStage) -> str:
    """Run-relative base name of a stage's ledger files: ``stages/0N-<stage>``."""
    return f"{STAGES_DIR}/{AGENT_STAGES.index(stage) + 1:02d}-{stage.name}"


def _input_hash(stage: AgentStage, prompt: str, run_dir: Path) -> str:
    """Hash of everything the stage reads: its prompt and its upstream artifacts."""
    digest = hashlib.sha256(prompt.encode("utf-8"))
    for dependency in stage.dependencies:
        for artifact in stage_by_name(dependency).artifacts:
            path = run_dir / artifact
            digest.update(artifact.encode("utf-8"))
            digest.update(_sha256_file(path).encode("utf-8") if path.is_file() else b"missing")
    return digest.hexdigest()


def _load_record(path: Path) -> StageRecord | None:
    if not path.is_file():
        return None
    try:
        return StageRecord.model_validate_json(path.read_text(encoding="utf-8"))
    except ValueError:
        return None


def _is_cached(prior: StageRecord | None, input_hash: str, run_dir: Path, stage: AgentStage) -> bool:
    if prior is None or prior.status not in {"completed", "cached"} or prior.input_hash != input_hash:
        return False
    try:
        return _artifact_hashes(run_dir, stage) == prior.artifact_hashes
    except RuntimeError:
        return False


class ToolCallingPipeline:
    def __init__(self, *, client: StageClient):
        self.client = client

    def _run_stage(
        self,
        stage: AgentStage,
        run_dir: Path,
        request: RunRequest,
        *,
        forced: bool,
        feedback: str | None,
        decisions_lock: threading.Lock,
    ) -> StageRecord:
        stem = _record_stem(stage)
        record_path = run_dir / f"{stem}.json"
        record_path.parent.mkdir(exist_ok=True)
        prior = _load_record(record_path)
        prompt = build_stage_prompt(stage, request, run_dir=run_dir, feedback=feedback)
        input_hash = _input_hash(stage, prompt, run_dir)
        record = StageRecord(
            name=stage.name,
            status="running",
            input_hash=input_hash,
            trace_path=f"{stem}-trace.json",
            result_path=f"{stem}-result.json",
            started_utc=_now(),
        )

        if not forced and _is_cached(prior, input_hash, run_dir, stage):
            record.status = "cached"
            record.artifact_hashes = prior.artifact_hashes
            record.tool_calls = prior.tool_calls
            record.completed_utc = _now()
            _write_json_atomic(record_path, record.model_dump_json(indent=2))
            return record

        _write_json_atomic(record_path, record.model_dump_json(indent=2))
        ctx = ToolContext(run_dir=run_dir, decisions_lock=decisions_lock)
        try:
            result = self.client.run_stage(
                stage_name=stage.name,
                prompt=prompt,
                tools=stage.tool_specs,
                ctx=ctx,
                reasoning_effort=request.reasoning_effort,
            )
            record.artifact_hashes = _artifact_hashes(run_dir, stage)
        except Exception as exc:  # noqa: BLE001 - record then re-raise
            record.status = "failed"
            record.error = str(exc)
            record.completed_utc = _now()
            _write_json_atomic(record_path, record.model_dump_json(indent=2))
            raise
        record.status = "completed"
        record.tool_calls = result.tool_calls
        record.completed_utc = _now()
        (run_dir / record.result_path).write_text(result.model_dump_json(indent=2), encoding="utf-8")
        (run_dir / record.trace_path).write_text(
            json.dumps({"call_log": ctx.call_log, "decisions": ctx.decisions}, indent=2),
            encoding="utf-8",
        )
        _write_json_atomic(record_path, record.model_dump_json(indent=2))
        return record

    def run(
        self,
        run_dir: Path,
        request: RunRequest,
        *,
        from_stage: str | None = None,
        feedback: dict[str, str] | None = None,
    ) -> PipelineResult:
        """Run every stage, honouring dependencies; force ``from_stage`` and its dependants."""
        run_dir = Path(run_dir)
        forced = stages_from(from_stage) if from_stage else frozenset()
        decisions_lock = threading.Lock()
        futures: dict[str, Future[StageRecord]] = {}

        def run_after_dependencies(stage: AgentStage) -> StageRecord:
            for dependency in stage.dependencies:
                futures[dependency].result()
            return self._run_stage(
                stage,
                run_dir,
                request,
                forced=stage.name in forced,
                feedback=(feedback or {}).get(stage.name),
                decisions_lock=decisions_lock,
            )

        with ThreadPoolExecutor(max_workers=len(AGENT_STAGES), thread_name_prefix="mimo-stage") as pool:
            for stage in AGENT_STAGES:
                futures[stage.name] = pool.submit(run_after_dependencies, stage)
            records = [futures[stage.name].result() for stage in AGENT_STAGES]

        return PipelineResult(
            artifacts=[artifact for stage in AGENT_STAGES for artifact in stage.artifacts],
            checks=[f"{record.name}:{record.status}" for record in records],
            notes=[f"MiMo 2.6 tool-calling pipeline finished ({len(records)} stages)"],
            tool_calls=[call for record in records for call in record.tool_calls],
            stage_records=[f"{_record_stem(stage)}.json" for stage in AGENT_STAGES],
        )
