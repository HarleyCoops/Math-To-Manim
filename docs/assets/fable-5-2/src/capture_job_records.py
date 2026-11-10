"""Capture real Mythos job records for the README diagrams.

Calls the MCP tool functions in ``mythos.mcp_server`` (``m2m_create_animation``
and ``m2m_get_job``) against a temporary run ledger. Nothing is written under
``runs/`` and no model is called:

- ``completed``: an offline run (``offline=True``; deterministic stand-in
  artifacts), polled until it finishes.
- ``running`` and ``failed``: a stub model backend answers the first three
  reasoning stages, waits at the fourth (math-director) while the job is
  polled, then raises. This is the crash the lifecycle commit records.

Each record is the JSON text the tool returned, unedited.

Usage:  .venv\\Scripts\\python.exe docs\\assets\\fable-5-2\\src\\capture_job_records.py
Writes: docs/assets/fable-5-2/src/data/job_records.json
"""

from __future__ import annotations

import json
import tempfile
import threading
import time
from pathlib import Path

from mythos import mcp_server
from mythos.harness import MythosHarness
from mythos.service import MythosService

OUT = Path(__file__).resolve().parent / "data" / "job_records.json"
PROMPT = "Why does a top precess?"


def poll(job_id: str) -> dict:
    return json.loads(mcp_server.m2m_get_job(job_id))


def wait_for(job_id: str, done, seconds: float = 30.0) -> dict:
    deadline = time.time() + seconds
    while True:
        record = poll(job_id)
        if done(record) or time.time() > deadline:
            return record
        time.sleep(0.05)


def main() -> None:
    records: dict[str, dict] = {}
    gate = threading.Event()
    calls = {"n": 0}

    def stub_model(prompt: str, **_: object) -> str:
        calls["n"] += 1
        if calls["n"] >= 4:
            gate.wait(30)
            raise RuntimeError("stub model backend stopped")
        return json.dumps({"stage_reply": calls["n"], "notes": "stub " * 60})

    def factory(**kwargs: object) -> MythosHarness:
        return MythosHarness(run_model=stub_model, model_fallbacks=(),
                             log=lambda _message: None, **kwargs)

    with tempfile.TemporaryDirectory() as tmp:
        mcp_server.set_service(MythosService(runs_dir=Path(tmp) / "mythos",
                                             harness_factory=factory))
        try:
            # 1. Offline run: completes; no render requested.
            created = json.loads(mcp_server.m2m_create_animation(
                mcp_server.CreateAnimationInput(prompt=PROMPT, offline=True)))
            records["completed"] = wait_for(
                created["id"], lambda r: r["status"] != "running")

            # 2. Stub backend: poll while it waits at math-director, then let it fail.
            time.sleep(1.1)  # a new second, so the run id needs no "-2" suffix
            created = json.loads(mcp_server.m2m_create_animation(
                mcp_server.CreateAnimationInput(prompt=PROMPT)))
            records["created"] = created
            records["running"] = wait_for(
                created["id"], lambda r: r["stage"] == "math-director")
            gate.set()
            records["failed"] = wait_for(
                created["id"], lambda r: r["status"] != "running")
        finally:
            gate.set()
            mcp_server.set_service(None)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(records, indent=2), encoding="utf-8")
    for name, rec in records.items():
        print(f"{name:>9} | status={rec['status']} stage={rec['stage']} "
              f"outcome={rec['outcome']} error={rec['error']}")


if __name__ == "__main__":
    main()
