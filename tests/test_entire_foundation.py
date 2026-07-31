"""Repository-level safety contract for ENTIRE integration."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_entire_routes_checkpoints_privately() -> None:
    """A public checkpoint remote or enabled telemetry would expose run data."""
    settings = json.loads(
        (ROOT / ".entire" / "settings.json").read_text(encoding="utf-8")
    )

    assert settings["enabled"] is True
    assert settings["external_agents"] is True
    assert settings["telemetry"] is False
    assert settings["strategy_options"]["checkpoint_remote"] == {
        "provider": "github",
        "repo": "HarleyCoops/math-to-manim-checkpoints",
    }
    assert settings["redaction"]["pii"] == {
        "enabled": True,
        "email": True,
        "phone": True,
        "address": False,
    }


def test_agent_hooks_are_project_scoped() -> None:
    """Removing a project hook must not silently disable session capture."""
    codex_hooks = json.loads(
        (ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8")
    )
    codex_config = tomllib.loads(
        (ROOT / ".codex" / "config.toml").read_text(encoding="utf-8")
    )
    claude_settings = json.loads(
        (ROOT / ".claude" / "settings.json").read_text(encoding="utf-8")
    )

    assert codex_config["features"]["hooks"] is True
    assert set(codex_hooks["hooks"]) == {
        "PostToolUse",
        "SessionStart",
        "Stop",
        "UserPromptSubmit",
    }
    assert set(claude_settings["hooks"]) == {
        "PostToolUse",
        "PreToolUse",
        "SessionEnd",
        "SessionStart",
        "Stop",
        "UserPromptSubmit",
    }


def test_entire_local_state_is_ignored() -> None:
    """Local logs, session bodies, and credentials must stay out of Git."""
    patterns = (ROOT / ".entire" / ".gitignore").read_text(
        encoding="utf-8"
    ).splitlines()

    assert "settings.local.json" in patterns
    assert "logs/" in patterns
    assert "m2m-sessions/" in patterns
    assert "tmp/" in patterns
