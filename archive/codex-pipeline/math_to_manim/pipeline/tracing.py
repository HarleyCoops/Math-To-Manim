"""JSONL tracing for local pipeline runs."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


class TraceWriter:
    def __init__(self, path: Path, enabled: bool = True):
        self.path = path
        self.enabled = enabled
        if enabled:
            path.parent.mkdir(parents=True, exist_ok=True)

    def event(self, stage: str, payload: dict[str, Any]) -> None:
        if not self.enabled:
            return
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "stage": stage,
            "payload": payload,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, default=str) + "\n")
