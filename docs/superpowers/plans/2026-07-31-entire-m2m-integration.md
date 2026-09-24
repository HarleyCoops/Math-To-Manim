# ENTIRE Native M2M Session Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` (recommended) or
> `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a provider-neutral `entire-agent-m2m` integration that
preserves Mythos, Sol, RL, and model-harness execution context as versioned,
queryable, training-ready ENTIRE sessions without coupling provider silos.

**Architecture:** Add a top-level `m2m_entire` package containing the canonical
event schema, fail-open local recorder, ENTIRE external-agent protocol adapter,
historical converters, RL wrapper, and privacy-filtered harness exporter.
Mythos and Sol emit lifecycle events through this neutral package; the
standalone RL environment remains isolated and is observed through a wrapper
that consumes its reward ledgers and result artifacts.

**Tech Stack:** Python 3.10+, Pydantic 2, JSONL, SHA-256, subprocess argument
arrays, ENTIRE external-agent protocol v1, pytest, GitHub Actions, upstream
`entireio/external-agents-tests` pinned at
`3220ca8cc7ba2fbfc5a951ce4a5937ca1a5ca26e`.

**Design:**
`docs/superpowers/specs/2026-07-31-entire-platform-integration-design.md`

## Global Constraints

- Begin only after the ENTIRE foundation plan has passed its milestone-one
  acceptance audit.
- Preserve the established `mythos/` and `sol/` provider-native boundaries.
- `sol/` must not import Mythos prompts, backends, or orchestration;
  `mythos/` must not import the Sol client.
- The standalone `environments/m2m2_visual_improvement` package must not import
  the root `mythos`, `sol`, or `m2m_entire` packages.
- Local `entire_session.jsonl` is written before any ENTIRE hook call.
- ENTIRE capture, upload, import, mirror, or search failure must not change a
  product, render, evaluation, or training result.
- Never serialize credentials, `.env`, authorization headers, raw binary
  media, weights, caches, or virtual environments.
- Store prompt/response text needed for training, but represent binary
  artifacts by relative path, MIME type, size, and SHA-256 only.
- Use explicit missing-data reasons; unavailable token counts are not zero.
- Resolve every transcript/artifact path beneath an approved root before read.
- Use no shell for plugin or hook subprocesses; enforce timeouts and output
  bounds.
- Stage commits by exact path and preserve unrelated RL/render work.
- Every task follows a failing-test, minimal-implementation, passing-test,
  exact-commit cycle.

---

### Task 1: Define the Versioned M2M Session Contract

**Files:**

- Create: `m2m_entire/__init__.py`
- Create: `m2m_entire/models.py`
- Create: `tests/test_m2m_entire_models.py`
- Modify: `pyproject.toml`

**Interfaces:**

- Consumes: Pydantic 2 already required by the root package.
- Produces: `M2MEvent`, `EventType`, `SessionKind`, `TokenUsage`,
  `ArtifactReference`, `RepositoryState`, and schema version
  `m2m.entire_session.v1`.

- [ ] **Step 1: Write the failing schema tests**

Create `tests/test_m2m_entire_models.py`:

```python
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from m2m_entire.models import (
    EVENT_SCHEMA_VERSION,
    ArtifactReference,
    EventType,
    M2MEvent,
    RepositoryState,
    SessionKind,
    TokenUsage,
)


def event() -> M2MEvent:
    return M2MEvent(
        schema_version=EVENT_SCHEMA_VERSION,
        event_id="evt-0001",
        event_type=EventType.SESSION_START,
        session_id="run-0001",
        session_kind=SessionKind.SOL_FILM,
        timestamp=datetime(2026, 7, 31, tzinfo=timezone.utc),
        repository=RepositoryState(
            commit="a" * 40,
            branch="codex/session-test",
            remote_url="https://github.com/HarleyCoops/Math-To-Manim.git",
            dirty_fingerprint="b" * 64,
        ),
        metadata={"provider": "openai", "model": "gpt-5.6-sol"},
    )


def test_event_round_trip_is_versioned() -> None:
    payload = event().model_dump_json()
    assert M2MEvent.model_validate_json(payload) == event()
    assert EVENT_SCHEMA_VERSION == "m2m.entire_session.v1"


def test_sha256_fields_are_strict() -> None:
    with pytest.raises(ValidationError):
        ArtifactReference(
            path="review.mp4",
            sha256="short",
            size_bytes=10,
            media_type="video/mp4",
        )


def test_missing_token_counts_require_a_reason() -> None:
    with pytest.raises(ValidationError):
        TokenUsage(input_tokens=None, output_tokens=None)
    usage = TokenUsage(
        input_tokens=None,
        output_tokens=None,
        unavailable_reason="provider did not expose usage",
    )
    assert usage.unavailable_reason == "provider did not expose usage"


def test_secret_like_metadata_keys_are_rejected() -> None:
    candidate = event().model_copy(update={"metadata": {"api_key": "value"}})
    with pytest.raises(ValidationError):
        M2MEvent.model_validate(candidate.model_dump())
```

- [ ] **Step 2: Run the tests to prove the package is absent**

```powershell
python -m pytest tests/test_m2m_entire_models.py -q
```

Expected: import failure for `m2m_entire`.

- [ ] **Step 3: Implement strict models**

Create `m2m_entire/models.py` with:

```python
from __future__ import annotations

from datetime import datetime
from enum import Enum, IntEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


EVENT_SCHEMA_VERSION = "m2m.entire_session.v1"
SHA256_PATTERN = r"^[0-9a-f]{64}$"
SECRET_KEYS = {
    "api_key", "authorization", "credential", "password", "secret", "token",
}


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class EventType(IntEnum):
    SESSION_START = 1
    TURN_START = 2
    TURN_END = 3
    COMPACTION = 4
    SESSION_END = 5
    SUBAGENT_START = 6
    SUBAGENT_END = 7


class SessionKind(str, Enum):
    MYTHOS_FILM = "mythos_film"
    SOL_FILM = "sol_film"
    RL_EXPERIMENT = "rl_experiment"
    RL_ROLLOUT = "rl_rollout"
    EVALUATION = "evaluation"
    HISTORICAL_IMPORT = "historical_import"


class TokenUsage(StrictModel):
    input_tokens: int | None = Field(default=None, ge=0)
    cached_input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    reasoning_tokens: int | None = Field(default=None, ge=0)
    api_call_count: int | None = Field(default=None, ge=0)
    unavailable_reason: str | None = None

    @model_validator(mode="after")
    def explain_missing_counts(self) -> "TokenUsage":
        if self.input_tokens is None or self.output_tokens is None:
            if not self.unavailable_reason:
                raise ValueError("missing token counts require unavailable_reason")
        return self


class ArtifactReference(StrictModel):
    path: str
    sha256: str = Field(pattern=SHA256_PATTERN)
    size_bytes: int = Field(ge=0)
    media_type: str


class RepositoryState(StrictModel):
    commit: str = Field(pattern=r"^[0-9a-f]{40}$")
    branch: str | None
    remote_url: str | None
    dirty_fingerprint: str = Field(pattern=SHA256_PATTERN)


class M2MEvent(StrictModel):
    schema_version: str = Field(pattern=r"^m2m\.entire_session\.v1$")
    event_id: str = Field(min_length=1)
    event_type: EventType
    session_id: str = Field(min_length=1)
    session_kind: SessionKind
    timestamp: datetime
    parent_session_id: str | None = None
    segment_id: str | None = None
    turn_id: str | None = None
    prompt: str | None = None
    response: str | None = None
    status: str | None = None
    repository: RepositoryState
    tokens: TokenUsage | None = None
    artifacts: tuple[ArtifactReference, ...] = ()
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def reject_secret_keys(self) -> "M2MEvent":
        stack: list[Any] = [self.metadata]
        while stack:
            value = stack.pop()
            if isinstance(value, dict):
                for key, child in value.items():
                    normalized = key.lower().replace("-", "_")
                    if normalized in SECRET_KEYS or normalized.endswith("_token"):
                        raise ValueError(f"secret-like metadata key: {key}")
                    stack.append(child)
            elif isinstance(value, list):
                stack.extend(value)
        return self
```

Export public symbols from `m2m_entire/__init__.py` and add `"m2m_entire*"` to
the existing `tool.setuptools.packages.find.include` list.

- [ ] **Step 4: Run focused and root tests**

```powershell
python -m pytest tests/test_m2m_entire_models.py -q
python -m pytest -q
```

Expected: pass.

- [ ] **Step 5: Commit the contract**

```powershell
git add -- `
  m2m_entire/__init__.py `
  m2m_entire/models.py `
  tests/test_m2m_entire_models.py `
  pyproject.toml
git diff --cached --check
git commit -m "feat: define Entire M2M session contract"
```

### Task 2: Implement Fail-open Local Recording and Hook Dispatch

**Files:**

- Create: `m2m_entire/recorder.py`
- Create: `tests/test_m2m_entire_recorder.py`

**Interfaces:**

- Consumes: `M2MEvent` and a run directory.
- Produces: `SessionRecorder.record(event: M2MEvent) -> CaptureResult`, local
  `entire_session.jsonl`, and optional `entire hooks m2m` dispatch.

- [ ] **Step 1: Write failing recorder tests**

```python
from datetime import datetime, timezone
from pathlib import Path

from m2m_entire.models import (
    EVENT_SCHEMA_VERSION,
    EventType,
    M2MEvent,
    RepositoryState,
    SessionKind,
)
from m2m_entire.recorder import CaptureResult, SessionRecorder


def event() -> M2MEvent:
    return M2MEvent(
        schema_version=EVENT_SCHEMA_VERSION,
        event_id="evt-0001",
        event_type=EventType.SESSION_START,
        session_id="run-0001",
        session_kind=SessionKind.SOL_FILM,
        timestamp=datetime(2026, 7, 31, tzinfo=timezone.utc),
        repository=RepositoryState(
            commit="a" * 40,
            branch="codex/session-test",
            remote_url="https://github.com/HarleyCoops/Math-To-Manim.git",
            dirty_fingerprint="b" * 64,
        ),
        metadata={"provider": "openai", "model": "gpt-5.6-sol"},
    )


class FailingHookRunner:
    def dispatch(self, hook_name: str, payload: bytes, timeout_seconds: float) -> None:
        raise TimeoutError("simulated hook timeout")


def test_local_event_survives_hook_failure(tmp_path: Path) -> None:
    recorder = SessionRecorder(tmp_path, hook_runner=FailingHookRunner())
    result = recorder.record(event())
    assert result.local_written is True
    assert result.remote_dispatched is False
    assert result.error == "TimeoutError: simulated hook timeout"
    stored = M2MEvent.model_validate_json(
        (tmp_path / "entire_session.jsonl").read_text().strip()
    )
    assert stored.event_id == "evt-0001"


def test_duplicate_event_id_is_idempotent(tmp_path: Path) -> None:
    recorder = SessionRecorder(tmp_path, hook_runner=None)
    first = recorder.record(event())
    second = recorder.record(event())
    assert first.local_written is True
    assert second.local_written is False
    assert len((tmp_path / "entire_session.jsonl").read_text().splitlines()) == 1
```

- [ ] **Step 2: Prove the tests fail**

```powershell
python -m pytest tests/test_m2m_entire_recorder.py -q
```

- [ ] **Step 3: Implement the recorder and subprocess adapter**

Implement:

```python
@dataclass(frozen=True)
class CaptureResult:
    local_written: bool
    remote_dispatched: bool
    error: str | None = None


class SubprocessHookRunner:
    def dispatch(
        self,
        hook_name: str,
        payload: bytes,
        timeout_seconds: float,
    ) -> None:
        subprocess.run(
            ["entire", "hooks", "m2m", hook_name],
            input=payload,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=True,
            timeout=timeout_seconds,
            shell=False,
        )


class SessionRecorder:
    def __init__(
        self,
        run_dir: Path,
        *,
        hook_runner: HookRunner | None,
        timeout_seconds: float = 2.0,
    ) -> None:
        self.run_dir = run_dir.resolve()
        self.hook_runner = hook_runner
        self.timeout_seconds = timeout_seconds

    def record(self, event: M2MEvent) -> CaptureResult:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        transcript = self.run_dir / "entire_session.jsonl"
        event_bytes = (event.model_dump_json() + "\n").encode("utf-8")
        existing_ids = _read_event_ids(transcript)
        if event.event_id in existing_ids:
            return CaptureResult(local_written=False, remote_dispatched=False)
        with transcript.open("ab", buffering=0) as handle:
            handle.write(event_bytes)
        if self.hook_runner is None:
            return CaptureResult(local_written=True, remote_dispatched=False)
        try:
            self.hook_runner.dispatch(
                _hook_name(event.event_type), event_bytes, self.timeout_seconds
            )
        except (OSError, subprocess.SubprocessError, TimeoutError) as exc:
            return CaptureResult(
                local_written=True,
                remote_dispatched=False,
                error=f"{type(exc).__name__}: {exc}",
            )
        return CaptureResult(local_written=True, remote_dispatched=True)
```

Define `HookRunner` as a `Protocol` exposing `dispatch(hook_name: str, payload:
bytes, timeout_seconds: float) -> None`; `SubprocessHookRunner` is its production
implementation.

Implement `_read_event_ids()` with streaming, malformed-line skipping plus a
bounded warning, and `_hook_name()` with exact protocol names. Never read or
write outside `run_dir`.

- [ ] **Step 4: Run tests and commit**

```powershell
python -m pytest tests/test_m2m_entire_recorder.py -q
python -m pytest -q
git add -- m2m_entire/recorder.py tests/test_m2m_entire_recorder.py
git commit -m "feat: record fail-open M2M sessions"
```

### Task 3: Implement the Mandatory External-agent Protocol

**Files:**

- Create: `m2m_entire/plugin.py`
- Create: `m2m_entire/protocol.py`
- Create: `tests/test_m2m_entire_protocol.py`
- Modify: `pyproject.toml`

**Interfaces:**

- Consumes: protocol version 1, `ENTIRE_REPO_ROOT`, JSON stdin, and command
  arguments.
- Produces: executable `entire-agent-m2m` and mandatory protocol subcommands.

- [ ] **Step 1: Write black-box failing tests**

Use `subprocess.run([sys.executable, "-m", "m2m_entire.plugin", *args])` with
isolated `ENTIRE_REPO_ROOT` and `ENTIRE_PROTOCOL_VERSION=1`. Cover:

```python
def test_info_declares_protocol_one_and_m2m_name() -> None:
    result = invoke("info")
    assert result["protocol_version"] == 1
    assert result["name"] == "m2m"
    assert result["capabilities"]["hooks"] is False


def test_detect_requires_installed_root_package(tmp_path: Path) -> None:
    assert invoke("detect", repo=tmp_path) == {"present": False}
    (tmp_path / "pyproject.toml").write_text('[project]\nname="math-to-manim"\n')
    assert invoke("detect", repo=tmp_path) == {"present": True}


def test_chunk_and_reassemble_round_trip() -> None:
    payload = b"alpha\nbeta\ngamma\n"
    chunks = invoke_bytes("chunk-transcript", payload, "--max-size", "6")
    restored = invoke_json_bytes("reassemble-transcript", chunks)
    assert restored == payload
```

Also cover `get-session-id`, `get-session-dir`, `resolve-session-file`,
`read-session`, `write-session`, `read-transcript`, invalid JSON, missing args,
protocol mismatch, and `format-resume-command`.

- [ ] **Step 2: Run tests to prove commands are absent**

```powershell
python -m pytest tests/test_m2m_entire_protocol.py -q
```

- [ ] **Step 3: Implement the mandatory command router**

`m2m_entire.protocol` defines strict request/response models and these handlers:

```python
PROTOCOL_VERSION = 1


def info() -> dict[str, object]:
    return {
        "protocol_version": 1,
        "name": "m2m",
        "type": "Math-To-Manim",
        "description": "Math-To-Manim product and RL session capture",
        "is_preview": True,
        "protected_dirs": ["runs", ".entire"],
        "hook_names": [],
        "capabilities": {
            "hooks": False,
            "transcript_analyzer": False,
            "transcript_preparer": False,
            "token_calculator": False,
            "text_generator": False,
            "hook_response_writer": False,
            "subagent_aware_extractor": False,
        },
    }


def session_dir(repo_root: Path) -> Path:
    return repo_root.resolve() / ".entire" / "m2m-sessions"


def session_file(repo_root: Path, session_id: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", session_id)
    if not safe or safe != session_id:
        raise ValueError("invalid session ID")
    return session_dir(repo_root) / f"{safe}.jsonl"
```

Implement transcript chunking as base64-encoded chunks no larger than the
requested positive maximum, exact byte reassembly, containment checks for all
paths, 10 MB stdin limit, JSON-only stdout for JSON commands, raw bytes only for
raw transcript commands, and errors on stderr with nonzero exit.

`format-resume-command` returns:

```json
{"command":"m2m-entire resume SESSION_ID"}
```

where `SESSION_ID` is the validated argument value.

- [ ] **Step 4: Register the console scripts**

Add to `[project.scripts]` in `pyproject.toml`:

```toml
entire-agent-m2m = "m2m_entire.plugin:main"
m2m-entire = "m2m_entire.cli:main"
```

Create a minimal `m2m_entire/cli.py` that supports `--version` and exits with a
clear message for commands added in Task 5.

- [ ] **Step 5: Verify editable installation and mandatory commands**

```powershell
python -m pip install -e ".[dev]"
entire-agent-m2m info
entire-agent-m2m detect
python -m pytest tests/test_m2m_entire_protocol.py -q
```

- [ ] **Step 6: Commit**

```powershell
git add -- `
  m2m_entire/plugin.py `
  m2m_entire/protocol.py `
  m2m_entire/cli.py `
  tests/test_m2m_entire_protocol.py `
  pyproject.toml
git commit -m "feat: implement Entire external agent protocol"
```

### Task 4: Add Hooks, Transcript Analysis, and Token Calculation

**Files:**

- Create: `m2m_entire/hooks.py`
- Create: `m2m_entire/transcript.py`
- Create: `tests/test_m2m_entire_hooks.py`
- Create: `tests/test_m2m_entire_transcript.py`
- Modify: `m2m_entire/protocol.py`

**Interfaces:**

- Consumes: canonical M2M JSONL and raw hook payloads.
- Produces: hook marker `.entire/m2m-agent.json`, normalized ENTIRE events,
  prompt/file/summary extraction, and token aggregation.

- [ ] **Step 1: Write failing hook lifecycle tests**

Cover exact mappings:

```python
EVENT_MAP = {
    "session-start": 1,
    "turn-start": 2,
    "turn-end": 3,
    "compaction": 4,
    "session-end": 5,
    "subagent-start": 6,
    "subagent-end": 7,
}
```

Assert `install-hooks` writes:

```json
{
  "enabled": true,
  "hook_command": "entire hooks m2m",
  "protocol_version": 1
}
```

Assert install is idempotent, uninstall removes only the marker, and malformed
or unrelated hook payloads return `null`.

- [ ] **Step 2: Write failing transcript tests**

Use three canonical events with prompt, artifact paths, token counts, and one
explicit unavailable reason. Assert:

- byte position equals file size;
- modified-file extraction returns normalized relative paths;
- prompt extraction preserves order;
- summary reports terminal status and counts;
- token calculation sums known fields and does not turn unavailable values into
  zeros;
- an artifact path escaping the repository is rejected.

- [ ] **Step 3: Prove failures**

```powershell
python -m pytest `
  tests/test_m2m_entire_hooks.py `
  tests/test_m2m_entire_transcript.py -q
```

- [ ] **Step 4: Implement hooks and analyzers**

`parse_hook(hook_name, raw)` validates the raw JSON as `M2MEvent` and returns:

```python
{
    "type": int(event.event_type),
    "session_id": event.session_id,
    "session_ref": str(transcript_path),
    "prompt": event.prompt,
    "model": str(event.metadata.get("model", "")),
    "timestamp": event.timestamp.isoformat(),
    "metadata": {
        "session_kind": event.session_kind.value,
        "event_id": event.event_id,
        "status": event.status,
    },
}
```

Add exact optional command handlers, then change `info()` to declare:

```json
{
  "hooks": true,
  "transcript_analyzer": true,
  "transcript_preparer": false,
  "token_calculator": true,
  "text_generator": false,
  "hook_response_writer": false,
  "subagent_aware_extractor": false
}
```

and list all seven hook names. Keep nested lifecycle event parsing even though
subagent-wide file/token aggregation remains false until a later protocol
revision is justified by fixtures.

- [ ] **Step 5: Run tests and enable the external agent locally**

```powershell
python -m pytest `
  tests/test_m2m_entire_hooks.py `
  tests/test_m2m_entire_transcript.py `
  tests/test_m2m_entire_protocol.py -q
entire agent add m2m
entire-agent-m2m are-hooks-installed
```

Expected: tests pass and hook marker reports installed.

- [ ] **Step 6: Commit**

```powershell
git add -- `
  m2m_entire/hooks.py `
  m2m_entire/transcript.py `
  m2m_entire/protocol.py `
  tests/test_m2m_entire_hooks.py `
  tests/test_m2m_entire_transcript.py
git commit -m "feat: capture M2M lifecycle hooks"
```

### Task 5: Add Diagnostics, Resume Routing, and Historical Conversion

**Files:**

- Create: `m2m_entire/cli.py`
- Create: `m2m_entire/importer.py`
- Create: `tests/test_m2m_entire_cli.py`
- Create: `tests/test_m2m_entire_importer.py`
- Create: `tests/fixtures/entire_m2m/mythos/`
- Create: `tests/fixtures/entire_m2m/sol/`
- Create: `tests/fixtures/entire_m2m/development_sessions/`
- Modify: `scripts/entire/session_inventory.py`

**Interfaces:**

- Consumes: Mythos and Sol run directories through filesystem-only adapters,
  plus the ignored milestone-one development-session reconciliation inventory.
- Produces: `m2m-entire doctor`, `backfill`, `reconcile-development`, and
  `resume`; deterministic `entire_session.jsonl`; explicit conversion reports.

- [ ] **Step 1: Create sanitized successful and failed run fixtures**

Use text-only copies of existing offline Mythos and Sol bundles. Each fixture
contains its provider's manifest, numbered artifacts, scene source, and one
failure variant. Remove absolute paths, timestamps identifying the machine,
raw agent transcripts, and secrets.

Add sanitized Codex and Claude JSONL fixtures representing one recoverable
parser failure and one irrecoverably malformed transcript. The fixture
inventory must contain the corresponding source paths, SHA-256 values, original
ENTIRE errors, and `import_status="parser_failure"`.

- [ ] **Step 2: Write failing importer tests**

Assert:

- provider detection is based on manifest/artifact shape;
- successful and failed runs both convert;
- event IDs are deterministic from provider, run ID, segment, and event index;
- artifact references use relative paths and correct hashes;
- conversion never imports `mythos` or `sol` modules;
- repeated backfill produces byte-identical JSONL and reports `already_present`;
- path escapes and malformed manifests produce structured failures.
- development-session reconciliation verifies the recorded source hash before
  reading, streams recoverable user/assistant/tool records into canonical
  `HISTORICAL_IMPORT` sessions, and never copies raw transcript bodies;
- irrecoverable or absent transcripts retain source path, expected hash, and
  exact terminal error with status `proven_unreadable` or `source_absent`;
- a second reconciliation is byte-identical and never duplicates events.

- [ ] **Step 3: Write failing CLI tests with injected command runners**

Cover:

```text
m2m-entire doctor --json
m2m-entire backfill --runs-dir runs --dry-run --json
m2m-entire backfill --runs-dir runs --json
m2m-entire reconcile-development --inventory .entire/tmp/session-import-inventory.json --dry-run --json
m2m-entire reconcile-development --inventory .entire/tmp/session-import-inventory.json --json
m2m-entire resume SESSION_ID
```

`resume` must return the existing `math-to-manim-sol resume RUN_ID` command for
Sol sessions, the RL resume command stored in metadata for resumable
experiments, and exit code 2 with `replay-only` for Mythos historical sessions.

- [ ] **Step 4: Implement filesystem-only conversion**

Public interfaces:

```python
@dataclass(frozen=True)
class ConversionResult:
    run_dir: Path
    provider: str | None
    session_id: str | None
    status: str
    event_count: int
    error: str | None
```

Implement `convert_run(run_dir: Path, *, dry_run: bool) -> ConversionResult`
and `scan_runs(runs_dir: Path, *, dry_run: bool) -> list[ConversionResult]` using
`Path.resolve()` and `is_relative_to()`, atomic temporary-file replacement,
deterministic event ordering, explicit failure records, and no provider imports.

Implement `reconcile_development_sessions(inventory_path: Path, *, dry_run:
bool) -> list[ConversionResult]`. For each `parser_failure`, resolve the source,
verify its recorded SHA-256, stream only recognized Codex or Claude JSONL record
shapes, and write the sanitized canonical transcript through the plugin's
`.entire/m2m-sessions` session API. Atomically update only disposition,
checkpoint ID, and error fields in the ignored inventory. If no prompt,
response, tool, or lifecycle record can be recovered, preserve the original
error and append the concrete unreadable reason instead of manufacturing a
session. Invoke `entire import m2m --session SESSION_ID` through an injected,
argument-array command runner only after a successful non-dry-run conversion.

`doctor --json` reports binary discovery, marker state, ENTIRE status, private
checkpoint configuration, writable local transcript roots, and protocol
version without credential values.

- [ ] **Step 5: Verify and commit**

```powershell
python -m pytest `
  tests/test_m2m_entire_cli.py `
  tests/test_m2m_entire_importer.py -q
m2m-entire doctor --json
m2m-entire backfill --runs-dir .tmp-runs --dry-run --json
m2m-entire reconcile-development `
  --inventory .entire/tmp/session-import-inventory.json `
  --dry-run --json
git add -- `
  m2m_entire/cli.py `
  m2m_entire/importer.py `
  scripts/entire/session_inventory.py `
  tests/test_m2m_entire_cli.py `
  tests/test_m2m_entire_importer.py `
  tests/fixtures/entire_m2m
git commit -m "feat: backfill historical M2M sessions"
```

### Task 6: Instrument Mythos without Changing Its Orchestration

**Files:**

- Modify: `mythos/harness.py`
- Create: `tests/test_mythos_entire_session.py`

**Interfaces:**

- Consumes: `SessionRecorder`, Mythos run ID, prompt, stage artifacts, manifest,
  render/repair outcomes.
- Produces: one parent Mythos session with stage turns and terminal event.

- [ ] **Step 1: Write the failing offline lifecycle test**

Construct `harness = MythosHarness(offline=True, runs_dir=tmp_path)`, call
`manifest = harness.run("the heat equation")`, parse
`tmp_path / manifest["run_id"] / "entire_session.jsonl"`, and assert this ordered
shape:

```python
EXPECTED_TURNS = (
    "intent",
    "cartographer",
    "curriculum",
    "math-director",
    "cinematographer",
    "scene-composer",
    "codegen",
    "validation",
)
```

Assert the first event is `SESSION_START`, every turn has start/end records,
the last event is `SESSION_END`, artifacts are hashed, and offline token usage
has the explicit reason `offline run made no model call`.

Add a forced-stage-failure test asserting terminal status `failed` while the
original `StageValidationError` still propagates unchanged.

- [ ] **Step 2: Prove the tests fail**

```powershell
python -m pytest tests/test_mythos_entire_session.py -q
```

- [ ] **Step 3: Add lifecycle emissions around existing boundaries**

Instantiate the neutral recorder only after `run_dir` exists. Emit:

```text
SessionStart before the first stage
TurnStart immediately before each existing stage call
TurnEnd after artifact validation and manifest write
TurnEnd(status=failed) from each stage exception path
render and repair turns around existing operations
SessionEnd(status=completed|failed) from the outer finally path
```

Do not move the stage loop, alter prompts, change fallback behavior, change
rendering, or make ENTIRE errors visible as Mythos failures. Derive event IDs
deterministically from `run_id`, stage name, attempt, and lifecycle edge.

- [ ] **Step 4: Run Mythos and boundary tests**

```powershell
python -m pytest `
  tests/test_mythos_entire_session.py `
  tests/test_harness_offline.py `
  tests/test_backends.py `
  tests/test_robustness.py -q
python -m pytest -q
```

- [ ] **Step 5: Commit**

```powershell
git add -- mythos/harness.py tests/test_mythos_entire_session.py
git commit -m "feat: capture Mythos product sessions"
```

### Task 7: Instrument Sol without Breaking Its Provider Silo

**Files:**

- Modify: `sol/harness.py`
- Modify: `sol/staged.py`
- Create: `tests/test_sol_entire_session.py`

**Interfaces:**

- Consumes: Sol `RunManifest`, `StageRecord`, trace paths, validation, render,
  review, repair, and resume state.
- Produces: one parent Sol session with durable specialist turns and linked
  resume segments.

- [ ] **Step 1: Write failing offline and resume lifecycle tests**

Assert the offline run records:

```python
EXPECTED_SOL_STAGES = (
    "intent",
    "cartographer",
    "curriculum",
    "math-director",
    "cinematographer",
    "scene-composer",
)
```

Then assert validation and terminal events, stage record/trace hashes, explicit
offline token reason, and one stable parent session ID. A resume test must keep
the same session ID, create a new segment ID, and link the segment to the prior
one without replacing earlier JSONL lines.

Add an AST/import assertion proving no module under `sol/` imports a module
whose root is `mythos`.

- [ ] **Step 2: Prove failure**

```powershell
python -m pytest tests/test_sol_entire_session.py -q
```

- [ ] **Step 3: Emit events at existing durable stage boundaries**

Use `StagedPipeline._run_stage` for stage turn start/end events and
`SolHarness.run`/`resume` for parent session/segment events. Preserve current
parallel stage execution; each event ID includes stage index and attempt so
concurrent completion order cannot change identity. Serialize events under a
file lock or append lock so parallel stages cannot interleave bytes.

Capture Codex trace files by relative path and SHA-256. Do not duplicate large
raw trace bodies into metadata; the canonical transcript already stores the
turn response needed for training.

- [ ] **Step 4: Run Sol, isolation, and root tests**

```powershell
python -m pytest `
  tests/test_sol_entire_session.py `
  tests/test_sol_silo.py `
  tests/test_sol_staged_pipeline.py -q
python -m pytest -q
```

- [ ] **Step 5: Commit**

```powershell
git add -- sol/harness.py sol/staged.py tests/test_sol_entire_session.py
git commit -m "feat: capture Sol product sessions"
```

### Task 8: Capture RL Experiments and Rollouts through a Wrapper

**Files:**

- Create: `m2m_entire/rl.py`
- Create: `tests/test_m2m_entire_rl.py`
- Create: `experiments/prime_rl/entire/README.md`
- Modify: `m2m_entire/cli.py`

**Interfaces:**

- Consumes: an external command argument array, experiment ID, output ledger
  directory, dataset/task/policy identifiers, and `RewardLedger` JSON files.
- Produces: parent RL experiment session, rollout child sessions, render/reward
  turns, and original command exit code.

- [ ] **Step 1: Write failing wrapper tests with a fake process runner**

Assert:

- commands remain argument arrays and never use a shell;
- session start is recorded before command execution;
- successful and failed commands preserve their exact exit code;
- reward components, aggregate reward, infrastructure exclusions, task ID,
  dataset version, split, seed, model, and policy checkpoint are captured;
- malformed ledgers create failed evidence events without converting an
  infrastructure failure to model reward zero;
- the standalone environment package is never imported.

- [ ] **Step 2: Prove failure**

```powershell
python -m pytest tests/test_m2m_entire_rl.py -q
```

- [ ] **Step 3: Implement the wrapper**

Public interface:

```python
@dataclass(frozen=True)
class ExperimentCommand:
    experiment_id: str
    argv: tuple[str, ...]
    ledger_dir: Path
    run_dir: Path
    model: str
    dataset_version: str
    split: str
    seed: int


@dataclass(frozen=True)
class ProcessResult:
    returncode: int
    stdout: str
    stderr: str
```

Define `ProcessRunner` as a protocol exposing `run(argv: tuple[str, ...], *,
shell: Literal[False]) -> ProcessResult`, and implement `SubprocessProcessRunner`
with `subprocess.run(list(argv), shell=False, capture_output=True, text=True,
check=False)`.

Implement `run_experiment(command: ExperimentCommand, *, runner: ProcessRunner,
recorder: SessionRecorder) -> int`. It must call
`runner.run(command.argv, shell=False)`, record terminal state from the actual
return code, scan only resolved JSON ledgers beneath `ledger_dir`, validate the
known reward-ledger schema without importing the environment, and record one
child session per rollout/task.

Add CLI syntax:

```text
m2m-entire rl-run --experiment-id EXPERIMENT_ID \
  --run-dir RUN_DIR --ledger-dir LEDGER_DIR --model MODEL \
  --dataset-version VERSION --split train --seed 7 -- COMMAND ARGUMENTS
```

- [ ] **Step 4: Run wrapper and existing RL schema tests**

```powershell
python -m pytest tests/test_m2m_entire_rl.py -q
uv run --project environments/m2m2_visual_improvement pytest `
  environments/m2m2_visual_improvement/tests/test_schemas.py `
  environments/m2m2_visual_improvement/tests/test_telemetry.py -q
```

The second file may still be user-owned uncommitted work; run it but do not
stage or modify it in this task.

- [ ] **Step 5: Commit only wrapper-owned files**

```powershell
git add -- `
  m2m_entire/rl.py `
  m2m_entire/cli.py `
  tests/test_m2m_entire_rl.py `
  experiments/prime_rl/entire/README.md
git commit -m "feat: capture RL experiment sessions"
```

### Task 9: Export Privacy-filtered Model-harness Examples

**Files:**

- Create: `m2m_entire/export.py`
- Create: `tests/test_m2m_entire_export.py`
- Modify: `m2m_entire/cli.py`

**Interfaces:**

- Consumes: canonical M2M session JSONL and private provenance identifiers.
- Produces: deterministic JSONL `HarnessExample` records for SFT, preference,
  failure-analysis, and reward-conditioned datasets.

- [ ] **Step 1: Write failing exporter tests**

Test that exports:

- keep source session ID, event IDs, schema version, source commit, prompt,
  response, status, artifact hashes, model identity, and known token/reward data;
- distinguish film stages, successful RL rollouts, failed rollouts, and
  infrastructure exclusions;
- reject records containing secret-like keys or credentialed URLs;
- normalize Windows profile paths to `$USERPROFILE`;
- exclude binary bodies and absolute ignored-file contents;
- sort deterministically and produce byte-identical output twice;
- never train on a missing response without an explicit failure label.

- [ ] **Step 2: Prove failure**

```powershell
python -m pytest tests/test_m2m_entire_export.py -q
```

- [ ] **Step 3: Implement strict export records**

Define:

```python
from typing import Literal

from pydantic import Field

from m2m_entire.models import StrictModel, TokenUsage


class HarnessExample(StrictModel):
    schema_version: Literal["m2m.harness_example.v1"]
    example_id: str
    source_session_id: str
    source_event_ids: tuple[str, ...]
    source_commit: str
    task_kind: str
    prompt: str
    response: str | None
    outcome: str
    model: str | None
    tokens: TokenUsage | None
    reward: float | None = Field(default=None, ge=0.0, le=1.0)
    reward_components: dict[str, float]
    artifact_hashes: tuple[str, ...]
```

The exporter accepts only explicit input transcript paths and output paths,
applies recursive secret-key and credentialed-URL rejection, normalizes local
paths, and writes through a temporary file plus atomic replacement.

Add:

```text
m2m-entire export-harness --input SESSION_JSONL --output DATASET_JSONL
```

- [ ] **Step 4: Verify and commit**

```powershell
python -m pytest tests/test_m2m_entire_export.py -q
python -m pytest -q
git add -- `
  m2m_entire/export.py `
  m2m_entire/cli.py `
  tests/test_m2m_entire_export.py
git commit -m "feat: export training-ready session examples"
```

### Task 10: Add Upstream Protocol Compliance CI

**Files:**

- Create: `.github/workflows/entire-m2m-agent.yml`
- Create: `tests/fixtures/entire_m2m/compliance.json`
- Create: `tests/test_entire_workflow.py`

**Interfaces:**

- Consumes: editable package installation and pinned upstream compliance action.
- Produces: mandatory and optional protocol compliance on pull requests and
  main pushes.

- [ ] **Step 1: Write a failing workflow contract test**

Assert YAML text contains:

```text
entireio/external-agents-tests@3220ca8cc7ba2fbfc5a951ce4a5937ca1a5ca26e
.venv/bin/entire-agent-m2m
tests/fixtures/entire_m2m/compliance.json
```

Also assert the workflow uses Python 3.12, installs `.[dev]`, runs local tests,
and has no secret/token environment keys.

- [ ] **Step 2: Prove failure**

```powershell
python -m pytest tests/test_entire_workflow.py -q
```

- [ ] **Step 3: Create the pinned compliance workflow**

Use this job structure:

```yaml
name: ENTIRE M2M Agent

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

jobs:
  protocol-compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - name: Install package
        run: |
          python -m venv .venv
          .venv/bin/python -m pip install -e ".[dev]"
      - name: Run local protocol tests
        run: .venv/bin/python -m pytest tests/test_m2m_entire_protocol.py -q
      - name: Run upstream compliance tests
        uses: entireio/external-agents-tests@3220ca8cc7ba2fbfc5a951ce4a5937ca1a5ca26e
        with:
          binary-path: ${{ github.workspace }}/.venv/bin/entire-agent-m2m
          fixtures-path: ${{ github.workspace }}/tests/fixtures/entire_m2m/compliance.json
```

The fixture points only to sanitized repository test data.

- [ ] **Step 4: Verify and commit**

```powershell
python -m pytest tests/test_entire_workflow.py -q
python -m pytest -q
git add -- `
  .github/workflows/entire-m2m-agent.yml `
  tests/fixtures/entire_m2m/compliance.json `
  tests/test_entire_workflow.py
git commit -m "ci: verify Entire M2M agent protocol"
```

### Task 11: Run Full Offline, Failure-injection, Backfill, and Live Verification

**Files:**

- Modify: `docs/ENTIRE_PLATFORM.md`
- Modify: `README.md` only to add a narrow ENTIRE link without altering the
  showcase GIFs or star chart.
- Create local ignored evidence under `.tmp-runs/entire-m2m-verification/`.
- Modify only implementation-owned files required to fix discovered failures.

**Interfaces:**

- Consumes: completed foundation, protocol adapter, instrumented products, RL
  wrapper, exporter.
- Produces: evidence for every milestone-two acceptance criterion and one live
  private ENTIRE M2M session.

- [ ] **Step 1: Run strict static and unit verification**

```powershell
git diff --check
python -m pytest -q
python -m compileall -q mythos sol m2m_entire
entire-agent-m2m info
m2m-entire doctor --json
```

- [ ] **Step 2: Run both offline product sessions**

```powershell
$verifyRoot = ".tmp-runs\entire-m2m-verification"
New-Item -ItemType Directory -Path $verifyRoot -Force | Out-Null
@'
from pathlib import Path
from mythos.harness import MythosHarness
MythosHarness(offline=True, runs_dir=Path(".tmp-runs/entire-m2m-verification/mythos")).run("the heat equation")
'@ | python -
@'
from pathlib import Path
from sol.harness import SolHarness
from sol.models import RunRequest
SolHarness(runs_dir=Path(".tmp-runs/entire-m2m-verification/sol")).run(RunRequest(prompt="why Fourier modes solve the heat equation", offline=True))
'@ | python -
```

Validate every created `entire_session.jsonl` with `M2MEvent` and verify
terminal events, stage shapes, artifact hashes, and explicit offline token
reasons.

- [ ] **Step 3: Run deterministic RL wrapper verification**

Use the committed small reward-ledger fixture and a command that exits zero:

```powershell
m2m-entire rl-run `
  --experiment-id entire-smoke `
  --run-dir "$verifyRoot\rl" `
  --ledger-dir "tests\fixtures\entire_m2m\rl-ledgers" `
  --model "fixture-policy" `
  --dataset-version "m2m2.visual_dataset_manifest.v1" `
  --split validation `
  --seed 7 `
  -- powershell -NoProfile -Command "exit 0"
```

Expected: experiment, rollout, reward, and terminal records validate.

- [ ] **Step 4: Inject hook failure and prove product equivalence**

Run both offline products once with a hook runner that raises timeout and once
with remote dispatch disabled. Compare all product artifacts except
`entire_session.jsonl` byte-for-byte. Exit codes and manifests must match.

- [ ] **Step 5: Backfill twice and prove idempotency**

```powershell
m2m-entire backfill --runs-dir $verifyRoot --dry-run --json
m2m-entire backfill --runs-dir $verifyRoot --json
m2m-entire backfill --runs-dir $verifyRoot --json
```

Expected: second real run reports every event already present and adds no JSONL
lines.

- [ ] **Step 6: Export and validate harness examples**

```powershell
$solTranscript = Get-ChildItem `
  -LiteralPath "$verifyRoot\sol" `
  -Recurse `
  -Filter "entire_session.jsonl" |
  Sort-Object LastWriteTimeUtc -Descending |
  Select-Object -First 1 -ExpandProperty FullName
if (-not $solTranscript) { throw "Sol verification transcript not found" }
m2m-entire export-harness `
  --input $solTranscript `
  --output "$verifyRoot\sol-harness.jsonl"
```

Validate every line as `HarnessExample`; scan for credentialed URLs, secret-like
keys, `C:\Users\chris`, binary encodings, and missing provenance.

- [ ] **Step 7: Run one live M2M session into the private checkpoint remote**

```powershell
entire agent add m2m
math-to-manim-sol run "explain why Fourier modes diagonalize diffusion" --offline
entire status
entire checkpoint list
git push
```

Inspect the resulting session in ENTIRE and verify:

- agent type is Math-To-Manim/m2m;
- parent session, turns, transcript, artifacts, model metadata, and tokens or
  unavailable reason appear;
- checkpoint ref exists in the private repository;
- public source repository still has no checkpoint ref.

- [ ] **Step 8: Update documentation without altering showcase assets**

Document plugin installation, `entire agent add m2m`, diagnostics, live capture,
backfill, resume semantics, RL wrapper, harness export, privacy, and fail-open
behavior. Add one README link under the technical reference area. Verify the
README's star chart and showcase media references remain unchanged with the
existing README tests.

- [ ] **Step 9: Run the completion audit**

```powershell
python -m pytest -q
uv run --project environments/m2m2_visual_improvement pytest -q
math-to-manim run "the heat equation" --offline
math-to-manim-sol run "why Fourier modes solve the heat equation" --offline
entire status
entire doctor
m2m-entire doctor --json
git ls-remote origin "refs/heads/entire/checkpoints/v1"
git status --short
```

Expected: suites pass, all diagnostics are healthy, public checkpoint lookup is
empty, and user-owned unrelated work is not staged.

- [ ] **Step 10: Commit documentation and any verified final fixes**

```powershell
git add -- docs/ENTIRE_PLATFORM.md README.md
git diff --cached --check
git commit -m "docs: document native Entire M2M sessions"
```

- [ ] **Step 11: Request review and report final evidence**

Use `superpowers:requesting-code-review`, resolve all critical findings, rerun
affected tests, and report:

- protocol compliance result;
- Mythos, Sol, RL, failure-injection, backfill, and export test counts;
- live M2M session and checkpoint IDs;
- historical conversion totals including failed runs;
- development-session reconciliation totals for recovered, proven unreadable,
  and absent sources;
- model-harness export example counts by task/outcome kind;
- private checkpoint evidence and public negative evidence;
- provider-boundary proof and remaining documented limitations.
