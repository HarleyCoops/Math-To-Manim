"""``math-to-manim-studio agent-check``: run one real agent through the runtime.

The Studio Doctor agent runs shell commands and returns one JSON object that
must match ``DOCTOR_SCHEMA``. A pass proves four things at once: the runtime
starts, the login works, the tool allow-list is applied, and structured
output comes back.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Callable

from studio.runtime import AgentRuntime, get_runtime, load_agent_file
from studio.settings import default_runs_dir

AGENTS_DIR = Path(__file__).resolve().parent / "agents"

_TEXT = {"type": ["string", "null"]}
_NUMBER = {"type": ["number", "null"]}
DOCTOR_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["os", "python", "pip_install_ok", "latex", "ffmpeg", "node",
                 "cpu_count", "memory_mb", "disk_free_mb"],
    "properties": {
        "os": _TEXT,
        "python": _TEXT,
        "pip_install_ok": {"type": ["boolean", "null"]},
        "latex": _TEXT,
        "ffmpeg": _TEXT,
        "node": _TEXT,
        "cpu_count": _NUMBER,
        "memory_mb": _NUMBER,
        "disk_free_mb": _NUMBER,
    },
}


def run_agent_check(*, runtime: AgentRuntime | None = None,
                    log: Callable[[str], None] = print) -> int:
    """Run the Studio Doctor agent and write ``doctor/agent-check.json``. 0 = pass."""
    runtime = runtime or get_runtime()
    spec = load_agent_file(AGENTS_DIR / "studio-doctor.md", tools=("Bash",),
                           schema=DOCTOR_SCHEMA)
    work = default_runs_dir() / "doctor" / "agent"
    work.mkdir(parents=True, exist_ok=True)
    log(f"agent-check: running {spec.name!r} on runtime {runtime.name!r} ...")
    result = runtime.run(spec, "Report the environment now.", cwd=work)
    record = asdict(result)
    (work.parent / "agent-check.json").write_text(json.dumps(record, indent=2),
                                                  encoding="utf-8")
    if result.ok:
        log(f"  [ok] model {result.model}, {result.turns} turns")
        log(json.dumps(result.output, indent=2))
        return 0
    log(f"  [FAILED] {result.error}")
    return 1
