"""Repair loop orchestration placeholders."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RepairLoopResult:
    attempts: int = 0
    applied_patches: list[str] = field(default_factory=list)
    stopped_reason: str = "not_started"


class RepairLoop:
    """Coordinates static, render, and visual repair budgets."""

    def __init__(self, max_static: int, max_render: int, max_visual: int):
        self.max_static = max_static
        self.max_render = max_render
        self.max_visual = max_visual

    def empty_result(self, reason: str) -> RepairLoopResult:
        return RepairLoopResult(stopped_reason=reason)
