"""JSONL trace capture: one event per action of a Mythos run.

A run's ``events.jsonl`` holds every model call, tool call, code version,
render attempt, QA check and repair loop, in order. The schema is fixed so
the traces can be published as a dataset::

    run_id, task_id, seq, ts, stage, event_type, model, runtime, profile,
    prompt_sha, input, output, tokens_in, tokens_out, latency_ms, parent_seq

Every event is scrubbed before it is written (:class:`Scrubber`): API keys,
tokens, home directory paths, user names and email addresses never reach the
file.

Two ways to attach:

- the harness holds a :class:`TraceWriter` and calls :meth:`TraceWriter.emit`;
- :func:`mythos.backends.run_model` reads the writer bound with
  :func:`bind` (a context variable) and records an ``agent_call`` for each
  model call it makes, so stage code needs no extra plumbing.
"""

from __future__ import annotations

import contextlib
import contextvars
import getpass
import hashlib
import json
import os
import re
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

EVENT_TYPES = (
    "agent_call",
    "tool_call",
    "code_version",
    "render_attempt",
    "qa_check",
    "repair_loop",
    "final",
)

EVENT_FIELDS = (
    "run_id", "task_id", "seq", "ts", "stage", "event_type", "model", "runtime",
    "profile", "prompt_sha", "input", "output", "tokens_in", "tokens_out",
    "latency_ms", "parent_seq",
)

#: Environment variable names whose values are treated as secrets.
_SECRET_ENV_NAME = re.compile(r"(KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|AUTH)", re.I)

_SECRET_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"sk-ant-[A-Za-z0-9_\-]{10,}"), "<secret>"),
    (re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}"), "<secret>"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"), "<secret>"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"), "<secret>"),
    (re.compile(r"\bhf_[A-Za-z0-9]{20,}"), "<secret>"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "<secret>"),
    (re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}"), "<secret>"),
    (re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}"), "<secret>"),
    (re.compile(r"\beyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}"), "<secret>"),
    (re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=\-]{16,}"), "Bearer <secret>"),
    (re.compile(
        r"(?i)\b([A-Za-z0-9_]*(?:api[_-]?key|access[_-]?token|auth[_-]?token|secret|password|passwd))"
        r"(\s*[:=]\s*[\"']?)([^\s\"',;]{8,})"),
     r"\1\2<secret>"),
)

_EMAIL = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")
# C:\Users\<name>, C:/Users/<name>, C:\\Users\\<name> (escaped), /home/<name>,
# /Users/<name>, /root.
_HOME_PATHS = (
    re.compile(r"[A-Za-z]:(?:\\\\|\\|/)+Users(?:\\\\|\\|/)+[^\\/\s\"'<>:|*?]+", re.I),
    re.compile(r"/(?:home|Users)/[^/\s\"'<>]+"),
    re.compile(r"/sessions/[^/\s\"'<>]+"),
)


@dataclass
class Scrubber:
    """Remove secrets and personal identifiers from trace content."""

    home_dirs: tuple[str, ...] = ()
    user_names: tuple[str, ...] = ()
    secrets: tuple[str, ...] = ()
    _names: list[re.Pattern[str]] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        names = sorted({n for n in self.user_names if n and len(n) >= 3},
                       key=len, reverse=True)
        self._names = [re.compile(rf"(?<![A-Za-z0-9]){re.escape(n)}(?![A-Za-z0-9])", re.I)
                       for n in names]
        self.home_dirs = tuple(sorted({h for h in self.home_dirs if h and len(h) > 3},
                                      key=len, reverse=True))
        self.secrets = tuple(sorted({s for s in self.secrets if s and len(s) >= 12},
                                    key=len, reverse=True))

    @classmethod
    def from_environment(cls, extra_names: tuple[str, ...] = ()) -> "Scrubber":
        """Names, home directory and secret values of this machine and process."""
        names: set[str] = set(extra_names)
        for candidate in (os.environ.get("USERNAME"), os.environ.get("USER")):
            if candidate:
                names.add(candidate)
        try:
            names.add(getpass.getuser())
        except Exception:  # noqa: BLE001 - no login name is fine
            pass
        home = str(Path.home())
        names.add(Path(home).name)
        homes = {home, home.replace("\\", "/"), home.replace("\\", "\\\\")}
        secrets = tuple(value for key, value in os.environ.items()
                        if _SECRET_ENV_NAME.search(key) and value and len(value) >= 12)
        return cls(home_dirs=tuple(homes), user_names=tuple(names), secrets=secrets)

    def text(self, value: str) -> str:
        for secret in self.secrets:
            value = value.replace(secret, "<secret>")
        for pattern, replacement in _SECRET_PATTERNS:
            value = pattern.sub(replacement, value)
        value = _EMAIL.sub("<email>", value)
        for home in self.home_dirs:
            value = value.replace(home, "~")
        for pattern in _HOME_PATHS:
            value = pattern.sub("~", value)
        for pattern in self._names:
            value = pattern.sub("<user>", value)
        return value

    def value(self, obj: Any) -> Any:
        """Scrub every string inside ``obj`` (dicts, lists, tuples), keys included."""
        if isinstance(obj, str):
            return self.text(obj)
        if isinstance(obj, dict):
            return {self.text(str(k)): self.value(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [self.value(v) for v in obj]
        return obj


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str | None:
    path = Path(path)
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _jsonable(obj: Any) -> Any:
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, Path):
        return str(obj)
    if hasattr(obj, "model_dump"):
        return _jsonable(obj.model_dump())
    return repr(obj)


class TraceWriter:
    """Append-only, thread-safe JSONL writer for one run."""

    def __init__(self, path: Path, *, run_id: str, task_id: str | None = None,
                 profile: str = "math", runtime: str = "local",
                 model: str | None = None, scrubber: Scrubber | None = None):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id
        self.task_id = task_id
        self.profile = profile
        self.runtime = runtime
        self.model = model
        self.scrubber = scrubber or Scrubber.from_environment()
        self._seq = 0
        self._lock = threading.Lock()
        self.tokens_in = 0
        self.tokens_out = 0
        self.counts: dict[str, int] = {}

    def emit(self, event_type: str, *, stage: str, input: Any = None,
             output: Any = None, model: str | None = None,
             tokens_in: int | None = None, tokens_out: int | None = None,
             latency_ms: float | None = None, parent_seq: int | None = None,
             prompt: str | None = None, runtime: str | None = None) -> int:
        """Write one event and return its ``seq``."""
        if event_type not in EVENT_TYPES:
            raise ValueError(f"unknown event type {event_type!r}")
        prompt_text = prompt if prompt is not None else (input if isinstance(input, str) else None)
        with self._lock:
            self._seq += 1
            seq = self._seq
            event = {
                "run_id": self.run_id,
                "task_id": self.task_id,
                "seq": seq,
                "ts": datetime.now(timezone.utc).isoformat(),
                "stage": stage,
                "event_type": event_type,
                "model": model if model is not None else self.model,
                "runtime": runtime or self.runtime,
                "profile": self.profile,
                "prompt_sha": sha256_text(prompt_text) if prompt_text else None,
                "input": _jsonable(input),
                "output": _jsonable(output),
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "latency_ms": round(latency_ms, 1) if latency_ms is not None else None,
                "parent_seq": parent_seq,
            }
            event = self.scrubber.value(event)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")
            self.tokens_in += tokens_in or 0
            self.tokens_out += tokens_out or 0
            self.counts[event_type] = self.counts.get(event_type, 0) + 1
            return seq

    def read(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines()
                if line.strip()]


# ---------------------------------------------------------------------- #
# The bound writer (read by backends.run_model)                           #
# ---------------------------------------------------------------------- #

@dataclass(frozen=True)
class Binding:
    writer: TraceWriter
    stage: str
    parent_seq: int | None = None


_BOUND: contextvars.ContextVar[Binding | None] = contextvars.ContextVar(
    "mythos_trace_binding", default=None)


def current() -> Binding | None:
    """The writer and stage bound for model calls in this context, if any."""
    return _BOUND.get()


@contextlib.contextmanager
def bind(writer: TraceWriter | None, stage: str,
         parent_seq: int | None = None) -> Iterator[None]:
    """Record every ``run_model`` call inside the block as ``stage``."""
    if writer is None:
        yield
        return
    token = _BOUND.set(Binding(writer, stage, parent_seq))
    try:
        yield
    finally:
        _BOUND.reset(token)


class Stopwatch:
    def __init__(self) -> None:
        self.start = time.perf_counter()

    @property
    def ms(self) -> float:
        return (time.perf_counter() - self.start) * 1000.0
