"""Pipeline state container."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PipelineState:
    run_dir: Path
    artifacts: dict[str, Any] = field(default_factory=dict)

    def put(self, name: str, artifact: Any) -> Any:
        self.artifacts[name] = artifact
        return artifact

    def get(self, name: str) -> Any:
        return self.artifacts[name]
